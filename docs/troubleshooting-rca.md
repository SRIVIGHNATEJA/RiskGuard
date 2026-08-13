# RiskGuard — Troubleshooting & Root Cause Analysis

**Document type**: Incident RCA (Test Engineering Evidence)  
**Project**: RiskGuard — ML-backed Insurance Risk Assessment  
**Author**: Phase 9 — Troubleshooting Lab  
**Based on**: Real failures encountered during development and testing

---

> **Key principle demonstrated throughout this document**:  
> *Symptom ≠ Root cause.*  
> The visible error message is always the starting point of investigation, never the conclusion.

---

## Incident 1 — `GET /claim/{id}` Always Returns 404 / MySQL Column Error

### Symptom

After the FastAPI backend was deployed (commit `cfae50d`), every call to  
`GET /claim/{id}` with a valid, existing claim ID returned an empty response or  
an internal server error — despite the claim having been successfully created  
by `POST /predict` moments earlier.

```
GET /claim/1
→ HTTP 500 Internal Server Error
```

When the MySQL query was isolated and executed directly, the database returned:

```
mysql.connector.errors.ProgrammingError:
1054 (42S22): Unknown column 'c.id' in 'where clause'
```

---

### Reproduction

1. Start backend: `uvicorn backend.main:app --host 127.0.0.1 --port 8000`
2. Submit a claim via `POST /predict` — returns `{"claim_id": 1, ...}` with HTTP 200
3. Immediately call `GET /claim/1`
4. **Expected**: HTTP 200 with full claim + risk result
5. **Actual**: HTTP 500 `{"detail": "Unexpected backend failure"}`

The `POST` worked. The data was in the database. The `GET` was broken.

---

### Layer Isolation

```
Client → FastAPI → [db.get_claim_with_result()] → MySQL
```

- **Client layer**: Request was correctly formed. Rule out client.
- **FastAPI routing layer**: Route matched, no routing error. Rule out routing.
- **ML service layer**: Not invoked on GET. Rule out ML.
- **Database layer**: Error message `1054 Unknown column 'c.id'` is a MySQL error.  
  **→ First divergence is in the SQL query inside `db.py`.**

---

### Root Cause Investigation

**Step 1** — Inspect the actual database schema:

```sql
-- sql/schema.sql (source of truth)
CREATE TABLE IF NOT EXISTS claims (
    claim_id INT AUTO_INCREMENT PRIMARY KEY,
    ...
);
```

The primary key column is named **`claim_id`**.

**Step 2** — Inspect the buggy query in `backend/db.py` (commit `cfae50d`):

```sql
SELECT
    c.id as claim_id,          -- ❌ column 'id' does not exist
    c.claim_amount,
    ...
FROM claims c
JOIN risk_results r ON c.id = r.claim_id    -- ❌
WHERE c.id = %s                              -- ❌
```

**Step 3** — Compare schema vs query:

| Schema definition | Query used |
|---|---|
| `claim_id` (PRIMARY KEY) | `c.id` |

The query was written assuming the primary key column was named `id` — a  
generic convention common in many ORM frameworks (Django, Rails, etc.).  
The RiskGuard schema explicitly named it `claim_id` for clarity and  
self-documentation. The query was never verified against the actual schema.

---

### Root Cause

> **Wrong column name in SQL query.**  
> The `GET /claim/{id}` query referenced `c.id` in three places.  
> The `claims` table schema defines the primary key as `claim_id`.  
> MySQL raised `1054 Unknown column 'c.id'` which FastAPI caught and  
> converted into a generic `500 Unexpected backend failure`.

The symptom (HTTP 500) masked the actual error (wrong SQL column name).  
Without reading the MySQL error log or isolating the DB layer directly,  
the symptom alone would have been misleading.

---

### Fix

**File**: `backend/db.py`  
**Commit**: `8bee9ed`  
**Change**: 3 lines modified

```diff
 SELECT
-    c.id as claim_id,
+    c.claim_id as claim_id,
     c.claim_amount,
     ...
 FROM claims c
-JOIN risk_results r ON c.id = r.claim_id
-WHERE c.id = %s
+JOIN risk_results r ON c.claim_id = r.claim_id
+WHERE c.claim_id = %s
```

Scope: **Minimum change** — only corrected the column name. No schema changes,  
no architecture changes, no new code added.

---

### Retest

After applying the fix:

```
GET /claim/1
→ HTTP 200 OK
→ {
    "claim_id": 1,
    "claim_amount": 10000.0,
    "previous_claim_count": 0,
    "days_since_last_claim": 365,
    "claim_category": "HOME",
    "risk_score": 0.0002,
    "prediction": "NORMAL"
  }
```

The JOIN between `claims` and `risk_results` on `claim_id` executed correctly.  
The response matched the data submitted via `POST /predict`.

---

### Final Result

| Item | Result |
|---|---|
| Symptom | HTTP 500 on `GET /claim/{id}` |
| Root cause | `c.id` used in query, schema defines `claim_id` |
| Fix | 3-line column name correction in `db.py` |
| Regression | `POST /predict` unaffected (INSERT did not use `c.id`) |
| Retest | HTTP 200, correct data returned |
| Lesson | Always verify SQL column names against the actual schema DDL, not assumed conventions |

---
---

## Incident 2 — ML Evaluation "Valid Boundary" Test Bypassed Application Validation

### Symptom

In Phase 8 (ML Product Testing), a test labelled  
**"Valid Application Boundary Test"** was documented as passing with:

```
claim_amount         : 999,999,999
previous_claim_count : 99
Application Stability: Did not crash.
```

This is a **test scope error**, not an ML model defect. Two separate facts must be  
kept distinct:

**Fact A — ML model behaviour (direct call)**:  
When `999,999,999` was fed directly to the sklearn pipeline via `joblib.load()`,  
the Logistic Regression sigmoid produced a probability of `1.0` and returned  
`prediction: REVIEW`. The ML model itself did **not** crash — the sigmoid function  
mathematically constrains all outputs to `[0.0, 1.0]` regardless of input magnitude.

**Fact B — Application behaviour (real API call)**:  
When the identical values were submitted through the real `POST /predict` endpoint,  
the application returned:

```
HTTP 500 Internal Server Error
{"detail": "Unexpected backend failure"}
```

The failure occurred at the **MySQL persistence layer**, not the ML model.  
`claim_amount DECIMAL(10,2)` accepts a maximum of `99,999,999.99`.  
Inserting `999,999,999.0` raised an out-of-range MySQL error.

The test was labelled as validating the *application* boundary.  
It only validated one layer (sklearn) of a four-layer system.

---

### Reproduction

**Test as originally run** (direct Python model call):
```python
model = joblib.load('models/risk_model.joblib')
extreme_df = pd.DataFrame([{'claim_amount': 999999999.0, ...}])
pred = model.predict(extreme_df)[0]   # → 'REVIEW', no crash
```

**Test run through the real application** (what was missing):
```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"claim_amount": 999999999.0, "previous_claim_count": 99, ...}'
```
```
HTTP 500 Internal Server Error
{"detail": "Unexpected backend failure"}
```

---

### Layer Isolation

```
Test script → [sklearn model directly] → Result
Test script → FastAPI → Pydantic → ML → MySQL → Result
```

- **Direct sklearn call**: Succeeded. Model output was `REVIEW`, risk_score `1.0`.
- **FastAPI Pydantic validation**: Passed — schema only enforces `ge=0`, no upper bound.
- **MySQL INSERT layer**: **Failed** — `claim_amount DECIMAL(10, 2)` has a maximum of  
  `99,999,999.99`. Inserting `999,999,999.0` raises an `Out of range value` MySQL error.
- **FastAPI exception handler**: Caught the MySQL error, returned generic HTTP 500.

**→ First divergence: the test script never called FastAPI or MySQL.**  
It called the sklearn pipeline object directly in Python memory.

---

### Root Cause

> **Test scope mismatch.**  
> The test was designed to evaluate the ML model's mathematical robustness  
> (sigmoid function always outputs [0, 1]).  
> It was labelled as an *application boundary test*.  
>
> An application boundary test must exercise the full stack:  
> `HTTP → Pydantic → ML → MySQL → HTTP response`.  
>
> A direct Python model call exercises only one layer of a 4-layer system.  
> The application failed at the MySQL persistence layer, which the original  
> test never reached.

The declared application limits are:

| Field | Declared max |
|---|---|
| `claim_amount` | 1,000,000 |
| `previous_claim_count` | 50 |
| `days_since_last_claim` | 3,650 |

These limits are not enforced by Pydantic (only `ge=0` is set).  
They are implicitly enforced by the MySQL `DECIMAL(10,2)` column type.

---

### Fix

**No application code was changed.**

The fix was to the *test*, not the application:

1. The original out-of-domain test was relabelled  
   **"Out-of-domain direct ML robustness observation"** in `ml_evaluation_evidence.txt`.

2. A new valid application boundary test was executed through the real `/predict` API:

```json
POST /predict
{
  "claim_amount": 1000000,
  "previous_claim_count": 50,
  "days_since_last_claim": 3650,
  "claim_category": "AUTO"
}
```

3. The fix commit was `2f3cf4c`.

---

### Retest

```
POST /predict (values = declared application maximums)
→ HTTP 200 OK
→ {"claim_id": 8, "risk_score": 1.0, "prediction": "REVIEW"}

Direct DB verification:
  claim_id=8, claim_amount=1000000.00, prediction=REVIEW  ✅
```

The application accepted the correct maximum-valid values through the full stack  
(HTTP → Pydantic → ML → MySQL → response).

---

### Final Result

| Item | Result |
|---|---|
| Symptom | "Valid boundary test passed" but real API returned HTTP 500 |
| Root cause | Test bypassed FastAPI, Pydantic, and MySQL — called sklearn directly |
| Fix | Relabelled out-of-domain test; ran correct boundary via `/predict` API |
| Retest | HTTP 200, DB persisted, all layers verified |
| Lesson | An application test must exercise the full stack. A unit-level component test is not an application test. |

---

## Summary

| | Incident 1 | Incident 2 |
|---|---|---|
| **Type** | SQL schema mismatch defect | Test scope mismatch |
| **Symptom** | HTTP 500 on GET | "Test passed" but API returned 500 |
| **First divergence** | SQL query vs schema column name | Test called sklearn directly, skipped HTTP/DB layers |
| **Root cause** | `c.id` vs `c.claim_id` | Test scope did not match "application boundary" claim |
| **Fix** | 3-line column name correction | Relabelled test; added real API boundary test |
| **Retest** | HTTP 200, JOIN verified | HTTP 200, DB persisted |
| **Evidence** | Git commits `cfae50d` → `8bee9ed` | Git commits `e78111f` → `2f3cf4c` |
| **Interview value** | Reading MySQL error logs; schema vs query verification | Distinguishing unit test vs integration test; layer isolation |
