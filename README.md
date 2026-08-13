# RiskGuard

**A QA laboratory built around an ML-powered insurance claim risk assessment application.**

RiskGuard is a small, self-contained project built for learning and demonstrating software testing skills. It is **not** a production insurance or fraud detection system. The dataset is entirely synthetic and has no actuarial validity.

---

## What It Is

RiskGuard provides a complete end-to-end testable system:

- A **FastAPI** backend with two endpoints
- A **Logistic Regression** ML model that classifies claim risk
- A **MySQL** database that persists every claim and its ML result
- A **vanilla HTML/CSS/JS** frontend for manual interaction
- A layered test suite covering manual QA, API testing, database validation, Selenium automation, and Playwright automation

The goal is to demonstrate that a QA engineer can test an ML-backed application across all its layers — not just the UI.

---

## Application Flow

```
User submits claim via UI
        ↓
  HTML/JS Frontend
        ↓
  POST /predict (FastAPI)
        ↓
  Pydantic schema validation
        ↓
  ML inference (Logistic Regression pipeline)
        ↓
  MySQL INSERT (claims + risk_results tables)
        ↓
  JSON response → UI displays result

User retrieves claim via UI
        ↓
  GET /claim/{id} (FastAPI)
        ↓
  MySQL JOIN query
        ↓
  JSON response → UI displays stored result
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| Validation | Pydantic v2 |
| ML | scikit-learn (Logistic Regression pipeline) |
| ML serialisation | joblib |
| Database | MySQL |
| DB client | mysql-connector-python |
| Frontend | HTML, CSS, vanilla JavaScript |
| UI automation (primary) | Python, Selenium, pytest |
| UI automation (secondary) | TypeScript, Playwright |
| API testing | Python requests, Postman collection |
| Environment | python-dotenv |

---

## ML Model

- **Algorithm**: Logistic Regression with a `StandardScaler + OneHotEncoder` preprocessing pipeline
- **Dataset**: 400 rows of synthetic claim data (`data/riskguard_synthetic_claims.csv`)
- **Features**: `claim_amount`, `previous_claim_count`, `days_since_last_claim`, `claim_category`
- **Target**: `risk_label` — either `NORMAL` or `REVIEW`
- **Train/test split**: 80/20, `random_state=42`, stratified
- **Saved pipeline**: `models/risk_model.joblib`
- **Test set accuracy**: 87.5% | Precision: 85.7% | Recall: 80.0% | F1: 82.8%

> ⚠️ The dataset is synthetic. These metrics reflect performance on synthetic data only and have no real-world meaning.

---

## API Endpoints

### `POST /predict`

Accepts a JSON claim, runs ML inference, persists to MySQL, returns the result.

**Request body:**
```json
{
  "claim_amount": 85000,
  "previous_claim_count": 5,
  "days_since_last_claim": 30,
  "claim_category": "AUTO"
}
```

Valid categories: `AUTO`, `HOME`, `HEALTH`, `LIFE`, `TRAVEL`

**Response (200):**
```json
{
  "claim_id": 1,
  "risk_score": 0.9959,
  "prediction": "REVIEW"
}
```

**Error responses**: `422` (missing/wrong-type field), `400` (invalid category), `500` (backend failure)

---

### `GET /claim/{id}`

Retrieves a previously submitted claim and its ML result from MySQL via a JOIN query.

**Response (200):**
```json
{
  "claim_id": 1,
  "claim_amount": 85000.0,
  "previous_claim_count": 5,
  "days_since_last_claim": 30,
  "claim_category": "AUTO",
  "risk_score": 0.9959,
  "prediction": "REVIEW"
}
```

**Error responses**: `404` (not found), `400` (non-numeric ID)

---

## Database Schema

Two tables with a foreign-key relationship:

```sql
claims       (claim_id PK, claim_amount, previous_claim_count,
              days_since_last_claim, claim_category, created_at)

risk_results (result_id PK, claim_id FK → claims.claim_id,
              risk_score, prediction, created_at)
```

Full DDL: [`sql/schema.sql`](sql/schema.sql)

---

## Testing Strategy

| Phase | What | Tools |
|---|---|---|
| Manual QA | 10 test cases across submit/retrieve/validation flows | Browser + docs |
| API testing | 6 tests covering 200/400/404/422 responses | Python requests + Postman |
| Database validation | INSERT verify, JOIN verify, API↔DB comparison, aggregation | MySQL + Python |
| Selenium (primary UI automation) | 4 tests: submit, retrieve, validation, negative | Python, Selenium, pytest |
| Playwright (secondary UI automation) | 4 tests + 1 debugging scenario | TypeScript, Playwright |
| ML product testing | Confusion matrix, precision/recall/F1, 3 behaviour scenarios, boundary test | Python, scikit-learn |
| Troubleshooting / RCA | 2 real incidents documented with root cause and retest | docs/troubleshooting-rca.md |

---

## Repository Structure

```
RiskGuard/
├── backend/
│   ├── main.py          # FastAPI app, route handlers
│   ├── schemas.py       # Pydantic request/response models
│   ├── ml_service.py    # ML inference singleton
│   └── db.py            # MySQL connection, INSERT, JOIN query
├── data/
│   └── riskguard_synthetic_claims.csv   # 400-row synthetic dataset
├── docs/
│   ├── manual-test-cases.md             # 10 manual QA test cases
│   ├── riskguard_postman_collection.json
│   ├── api_db_validation_evidence.txt   # Executed API + DB validation results
│   ├── ml_evaluation_evidence.txt       # Confusion matrix, metrics, behaviour tests
│   ├── troubleshooting-rca.md           # Root cause analysis for 2 real incidents
│   ├── run_api_db_validations.py        # Script used to generate API/DB evidence
│   ├── run_ml_evaluation.py             # Script used to generate ML evaluation evidence
│   ├── sql_interview_drills.sql         # SQL practice queries (not project tests)
│   └── screenshots/                     # Manual QA screenshots
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── ml/
│   ├── train.py         # Training script — produces models/risk_model.joblib
│   └── inspect_data.py  # Data inspection helper
├── models/
│   └── risk_model.joblib   # Saved sklearn pipeline (preprocessing + classifier)
├── sql/
│   └── schema.sql       # MySQL DDL
├── tests/
│   ├── selenium/
│   │   ├── conftest.py  # pytest fixture: Chrome WebDriver setup/teardown
│   │   └── test_ui.py   # 4 Selenium UI tests
│   └── playwright/
│       ├── playwright.config.ts
│       ├── ui.spec.ts   # 4 Playwright tests + 1 debugging scenario
│       └── package.json
├── requirements.txt     # Python dependencies
├── .gitignore
└── README.md
```

---

## Local Setup

### Prerequisites

- Python 3.10+
- MySQL 8.0+ running locally
- Node.js 18+ (for Playwright)
- Chrome browser (for Selenium and Playwright)
- ChromeDriver matching your Chrome version (for Selenium)

### 1. Clone and create virtual environment

```bash
git clone https://github.com/SRIVIGHNATEJA/RiskGuard.git
cd RiskGuard
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root (never commit this):

```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=riskguard_user
DB_PASSWORD=your_password_here
DB_NAME=riskguard
```

### 3. Set up MySQL database

```bash
mysql -u root -p < sql/schema.sql
```

Create the application user:

```sql
CREATE USER 'riskguard_user'@'localhost' IDENTIFIED BY 'your_password_here';
GRANT ALL PRIVILEGES ON riskguard.* TO 'riskguard_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Train the ML model

```bash
python3 ml/train.py
```

This produces `models/risk_model.joblib`. The file is committed — you only need to retrain if you change the dataset or model.

### 5. Install Playwright dependencies

```bash
cd tests/playwright
npm install
npx playwright install chromium
cd ../..
```

---

## Running the Application

### Start backend

```bash
source .venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### Start frontend

```bash
cd frontend
python3 -m http.server 8080 -b 127.0.0.1
```

Open `http://127.0.0.1:8080` in your browser.

---

## Running Tests

### Selenium (primary UI automation)

Both backend and frontend must be running.

```bash
source .venv/bin/activate
pytest tests/selenium/ -v
```

4 tests: successful submission, claim retrieval, input validation, negative/nonexistent ID.

### Playwright (secondary UI automation)

Both backend and frontend must be running.

```bash
cd tests/playwright
npx playwright test
```

4 tests mirroring the Selenium suite, plus one documented debugging scenario.

### API + Database validation

Backend must be running. MySQL must be accessible.

```bash
source .venv/bin/activate
python3 docs/run_api_db_validations.py
```

Runs 6 API tests and 5 database validations, printing results to stdout. Output is also saved in `docs/api_db_validation_evidence.txt`.

### ML evaluation

No servers needed — runs against the saved model and held-out test data.

```bash
source .venv/bin/activate
python3 docs/run_ml_evaluation.py
```

Output is also saved in `docs/ml_evaluation_evidence.txt`.

---

## Evidence Files

| File | Contents |
|---|---|
| `docs/manual-test-cases.md` | 10 structured manual test cases (ID, steps, expected, actual) |
| `docs/api_db_validation_evidence.txt` | Actual API responses and DB query output |
| `docs/ml_evaluation_evidence.txt` | Confusion matrix, classification report, behaviour tests, boundary test |
| `docs/troubleshooting-rca.md` | RCA for 2 real incidents: SQL column name defect + ML test scope error |
| `docs/riskguard_postman_collection.json` | Importable Postman v2.1 collection (6 requests) |
| `docs/screenshots/` | Manual QA screenshots (submit success, retrieve success, validation failure, not found) |

---

## Limitations and Scope

- **Synthetic data only.** The 400-row dataset was generated programmatically. It has no real actuarial or insurance validity.
- **No authentication.** The API is open. This is intentional — it is a QA lab, not a production service.
- **Single ML model.** Only Logistic Regression is used. No hyperparameter tuning or model comparison was performed.
- **Local development only.** There is no Docker, CI/CD, cloud deployment, or environment management beyond a local `.env` file.
- **Pydantic validation only enforces `ge=0` on numeric fields.** The upper application limits (`claim_amount ≤ 1,000,000`, etc.) are documented but not enforced by Pydantic — they are implicitly bounded by the MySQL `DECIMAL(10,2)` column type.
- **Selenium requires a matching ChromeDriver** installed and available on your `PATH`.

---

## Project Purpose

RiskGuard was built as a structured QA learning exercise to demonstrate:

1. Testing an ML-backed REST API at every layer (HTTP, validation, ML inference, DB persistence)
2. Writing and executing a layered test strategy (manual → API → DB → UI automation)
3. Using two distinct UI automation stacks (Selenium + Playwright) and understanding the differences
4. Applying root cause analysis methodology to real failures encountered during development
5. Maintaining clean repository hygiene and professional Git history

It is explicitly **not** a production system, a fraud detection engine, or a commercially deployed application.