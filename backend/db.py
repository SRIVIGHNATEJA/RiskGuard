import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "riskguard")
        )
        if connection.is_connected():
            return connection
    except Error as e:
        logger.error(f"Error while connecting to MySQL: {e}")
        raise RuntimeError("Database connection failed") from e

def insert_claim_and_result(claim_data: dict, risk_score: float, prediction: str) -> int:
    connection = get_db_connection()
    cursor = connection.cursor()
    claim_id = None
    
    try:
        # Start Transaction
        connection.start_transaction()

        # 1. Insert into claims
        insert_claim_query = """
            INSERT INTO claims (claim_amount, previous_claim_count, days_since_last_claim, claim_category)
            VALUES (%s, %s, %s, %s)
        """
        claim_values = (
            claim_data['claim_amount'],
            claim_data['previous_claim_count'],
            claim_data['days_since_last_claim'],
            claim_data['claim_category']
        )
        cursor.execute(insert_claim_query, claim_values)
        claim_id = cursor.lastrowid

        # 2. Insert into risk_results
        insert_risk_query = """
            INSERT INTO risk_results (claim_id, risk_score, prediction)
            VALUES (%s, %s, %s)
        """
        risk_values = (claim_id, risk_score, prediction)
        cursor.execute(insert_risk_query, risk_values)

        # Commit Transaction
        connection.commit()
        return claim_id

    except Error as e:
        # Rollback on error
        connection.rollback()
        logger.error(f"Transaction failed, rolled back: {e}")
        raise RuntimeError("Failed to insert claim and risk result") from e
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_claim_with_result(claim_id: int) -> dict:
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        query = """
            SELECT 
                c.claim_id as claim_id, 
                c.claim_amount, 
                c.previous_claim_count, 
                c.days_since_last_claim, 
                c.claim_category,
                r.risk_score, 
                r.prediction
            FROM claims c
            JOIN risk_results r ON c.claim_id = r.claim_id
            WHERE c.claim_id = %s
        """
        cursor.execute(query, (claim_id,))
        result = cursor.fetchone()
        return result
    except Error as e:
        logger.error(f"Error fetching claim: {e}")
        raise RuntimeError("Failed to fetch claim") from e
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
