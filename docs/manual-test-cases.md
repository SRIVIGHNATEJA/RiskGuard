# RiskGuard — Manual Test Suite

This document records the first execution of manual test cases against the RiskGuard API and Frontend integration.

## Test 1: Valid claim submission — AUTO
- **Preconditions:** Frontend and API running. MySQL database accessible.
- **Steps:** 
  1. Open UI. 
  2. Enter Amount: 85000, Count: 5, Days: 30, Category: AUTO. 
  3. Click "Predict Risk".
- **Test Data:** `{"claim_amount": 85000, "previous_claim_count": 5, "days_since_last_claim": 30, "claim_category": "AUTO"}`
- **Expected Result:** API returns 200 OK. UI displays Success, a Risk Score, and a Prediction. MySQL creates records.
- **Actual Result:** API returned 200 OK. UI rendered Success with Claim ID and Risk Score (approx 99.55%).
- **Status:** PASS

## Test 2: Valid claim submission — HOME
- **Preconditions:** System running.
- **Steps:** 
  1. Open UI. 
  2. Enter Amount: 1500, Count: 0, Days: 500, Category: HOME. 
  3. Click "Predict Risk".
- **Test Data:** `{"claim_amount": 1500, "previous_claim_count": 0, "days_since_last_claim": 500, "claim_category": "HOME"}`
- **Expected Result:** API returns 200 OK. UI displays Success and Prediction.
- **Actual Result:** API returned 200 OK. Claim successfully predicted (low risk score).
- **Status:** PASS

## Test 3: Minimum/boundary claim amount
- **Preconditions:** System running.
- **Steps:** Submit form with claim amount exactly 0.
- **Test Data:** `{"claim_amount": 0, "previous_claim_count": 1, "days_since_last_claim": 100, "claim_category": "HEALTH"}`
- **Expected Result:** Accepted (0 is a valid boundary).
- **Actual Result:** 200 OK. Success displayed.
- **Status:** PASS

## Test 4: Maximum/boundary claim amount
- **Preconditions:** System running.
- **Steps:** Submit form with very high claim amount (1,000,000).
- **Test Data:** `{"claim_amount": 1000000, "previous_claim_count": 0, "days_since_last_claim": 100, "claim_category": "TRAVEL"}`
- **Expected Result:** Accepted and processed normally by ML.
- **Actual Result:** 200 OK. High risk score calculated successfully.
- **Status:** PASS

## Test 5: Negative claim amount
- **Preconditions:** System running.
- **Steps:** Bypass HTML5 input step and submit -100 for amount.
- **Test Data:** `{"claim_amount": -100, "previous_claim_count": 0, "days_since_last_claim": 10, "claim_category": "AUTO"}`
- **Expected Result:** API returns 422 Unprocessable Entity due to Pydantic constraint (`ge=0`). UI displays Error.
- **Actual Result:** API returned 422. UI displayed validation error correctly.
- **Status:** PASS

## Test 6: Missing required field
- **Preconditions:** System running.
- **Steps:** Remove 'required' attribute from previous_claim_count via DevTools, leave blank, and submit.
- **Test Data:** Payload missing `previous_claim_count`.
- **Expected Result:** API returns 422 Unprocessable Entity. UI displays Error.
- **Actual Result:** API returned 422. Field required error displayed on UI.
- **Status:** PASS

## Test 7: Invalid claim category
- **Preconditions:** System running.
- **Steps:** Submit via API/Curl or intercept request to send category "FAKE".
- **Test Data:** `{"claim_amount": 100, "previous_claim_count": 0, "days_since_last_claim": 10, "claim_category": "FAKE"}`
- **Expected Result:** API returns 400 Bad Request (Business-rule violation). UI displays custom Error.
- **Actual Result:** API returned 400. UI displayed "Invalid claim_category".
- **Status:** PASS

## Test 8: Valid claim retrieval
- **Preconditions:** Claim ID 1 exists in database.
- **Steps:** Enter '1' in Claim ID field and click Retrieve.
- **Test Data:** `claim_id = 1`
- **Expected Result:** 200 OK. UI populates with claim features and risk results.
- **Actual Result:** 200 OK. Data successfully hydrated into UI fields.
- **Status:** PASS

## Test 9: Nonexistent claim retrieval
- **Preconditions:** System running.
- **Steps:** Enter '99999' in Claim ID field and click Retrieve.
- **Test Data:** `claim_id = 99999`
- **Expected Result:** 404 Not Found. UI displays Error.
- **Actual Result:** 404 returned. UI displayed "Claim not found".
- **Status:** PASS

## Test 10: Invalid claim ID format
- **Preconditions:** System running.
- **Steps:** Enter 'abc' in Claim ID field and click Retrieve.
- **Test Data:** `claim_id = abc`
- **Expected Result:** 400 Bad Request. UI displays Error.
- **Actual Result:** 400 returned. UI displayed "Invalid ID format".
- **Status:** PASS
