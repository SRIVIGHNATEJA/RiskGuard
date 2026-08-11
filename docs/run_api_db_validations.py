import requests
import json
import mysql.connector
import os
from dotenv import load_dotenv

# Load env variables for MySQL
load_dotenv()
MYSQL_USER = os.getenv("DB_USER", "riskguard_user")
MYSQL_PASSWORD = os.getenv("DB_PASSWORD", "SuperSecurePass123")
MYSQL_DB = os.getenv("DB_NAME", "riskguard")
MYSQL_HOST = os.getenv("DB_HOST", "127.0.0.1")

API_URL = "http://127.0.0.1:8000"

def run_api_tests():
    print("="*50)
    print("API TESTING EVIDENCE")
    print("="*50)
    
    # 1. Valid POST
    print("\n1. POST /predict - valid request")
    res1 = requests.post(f"{API_URL}/predict", json={
        "claim_amount": 10000.0,
        "previous_claim_count": 0,
        "days_since_last_claim": 365,
        "claim_category": "HOME"
    })
    print(f"Status: {res1.status_code} (Expected: 200)")
    print(f"Response: {json.dumps(res1.json(), indent=2)}")
    valid_claim_id = res1.json().get("claim_id")
    
    # 2. Missing required field
    print("\n2. POST /predict - missing required field")
    res2 = requests.post(f"{API_URL}/predict", json={
        "claim_amount": 10000.0,
        "claim_category": "HOME"
    })
    print(f"Status: {res2.status_code} (Expected: 422)")
    print(f"Response: {json.dumps(res2.json(), indent=2)}")
    
    # 3. Invalid data type
    print("\n3. POST /predict - invalid data type")
    res3 = requests.post(f"{API_URL}/predict", json={
        "claim_amount": "ONE THOUSAND",
        "previous_claim_count": 0,
        "days_since_last_claim": 365,
        "claim_category": "HOME"
    })
    print(f"Status: {res3.status_code} (Expected: 422)")
    print(f"Response: {json.dumps(res3.json(), indent=2)}")

    # 4. Invalid business value/category
    print("\n4. POST /predict - invalid business value")
    res4 = requests.post(f"{API_URL}/predict", json={
        "claim_amount": -500.0,
        "previous_claim_count": 0,
        "days_since_last_claim": 365,
        "claim_category": "UNKNOWN"
    })
    print(f"Status: {res4.status_code} (Expected: 400 or 422)")
    print(f"Response: {json.dumps(res4.json(), indent=2)}")
    
    # 5. GET /claim/{id}
    print(f"\n5. GET /claim/{valid_claim_id} - valid existing ID")
    res5 = requests.get(f"{API_URL}/claim/{valid_claim_id}")
    print(f"Status: {res5.status_code} (Expected: 200)")
    print(f"Response: {json.dumps(res5.json(), indent=2)}")
    
    # 6. GET /claim/999999
    print("\n6. GET /claim/999999 - nonexistent ID")
    res6 = requests.get(f"{API_URL}/claim/999999")
    print(f"Status: {res6.status_code} (Expected: 404)")
    print(f"Response: {json.dumps(res6.json(), indent=2)}")

    return valid_claim_id

def run_db_validations(claim_id):
    print("\n" + "="*50)
    print("DATABASE VALIDATION & CROSS-LAYER EVIDENCE")
    print("="*50)
    
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
    cursor = conn.cursor(dictionary=True)
    
    # 1. Verify submitted data exists
    print(f"\nDB Validation 1: Check claim_id {claim_id} in claims table")
    cursor.execute("SELECT * FROM claims WHERE claim_id = %s", (claim_id,))
    claim = cursor.fetchone()
    print(f"Found Claim: {claim}")
    
    # 2. Verify risk_results exists
    print(f"\nDB Validation 2: Check claim_id {claim_id} in risk_results table")
    cursor.execute("SELECT * FROM risk_results WHERE claim_id = %s", (claim_id,))
    result = cursor.fetchone()
    print(f"Found Result: {result}")
    
    # 3. JOIN claims and risk_results
    print("\nDB Validation 3: JOIN claims and risk_results")
    join_query = """
    SELECT c.claim_id, c.claim_amount, r.risk_score, r.prediction 
    FROM claims c 
    INNER JOIN risk_results r ON c.claim_id = r.claim_id 
    WHERE c.claim_id = %s
    """
    cursor.execute(join_query, (claim_id,))
    joined = cursor.fetchone()
    print(f"Joined Output: {joined}")
    
    # 4. Compare API vs DB (Cross-layer validation)
    print("\nDB Validation 4: Cross-Layer Comparison (API vs DB)")
    res = requests.get(f"{API_URL}/claim/{claim_id}").json()
    print(f"API Output    : amount={res['claim_amount']}, risk_score={res['risk_score']}")
    print(f"DB Output     : amount={joined['claim_amount']}, risk_score={joined['risk_score']}")
    if float(res['claim_amount']) == float(joined['claim_amount']):
        print("MATCH VALIDATED: API precisely matches Database State.")
    else:
        print("DISCREPANCY DETECTED.")
        
    # 5. Aggregation Query
    print("\nDB Validation 5: Aggregation over stored claims/results")
    agg_query = """
    SELECT c.claim_category, COUNT(c.claim_id) as total_claims, AVG(r.risk_score) as avg_risk
    FROM claims c
    INNER JOIN risk_results r ON c.claim_id = r.claim_id
    GROUP BY c.claim_category
    HAVING total_claims > 0
    ORDER BY avg_risk DESC;
    """
    cursor.execute(agg_query)
    aggs = cursor.fetchall()
    for row in aggs:
        print(f"Category: {row['claim_category']} | Count: {row['total_claims']} | Avg Risk: {float(row['avg_risk']):.4f}")
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    cid = run_api_tests()
    run_db_validations(cid)
