-- RISKGuard QA Lab
-- Task 1.1: MySQL Database Schema Definition

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS riskguard;
USE riskguard;

-- Table 1: claims
-- Represents the incoming claim data received from the API.
CREATE TABLE IF NOT EXISTS claims (
    claim_id INT AUTO_INCREMENT PRIMARY KEY,
    claim_amount DECIMAL(10, 2) NOT NULL,
    previous_claim_count INT NOT NULL,
    days_since_last_claim INT NOT NULL,
    claim_category VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_claim_amount CHECK (claim_amount >= 0),
    CONSTRAINT chk_previous_claim_count CHECK (previous_claim_count >= 0),
    CONSTRAINT chk_days_since_last_claim CHECK (days_since_last_claim >= 0),
    CONSTRAINT chk_claim_category CHECK (claim_category IN ('Auto', 'Home', 'Health', 'Life', 'Travel'))
);

-- Table 2: risk_results
-- Represents the ML prediction result associated with a claim.
CREATE TABLE IF NOT EXISTS risk_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    claim_id INT NOT NULL,
    risk_score DECIMAL(5, 4) NOT NULL,
    prediction VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_risk_score CHECK (risk_score >= 0.0 AND risk_score <= 1.0),
    CONSTRAINT chk_prediction CHECK (prediction IN ('NORMAL', 'REVIEW')),
    CONSTRAINT fk_claims_risk_results FOREIGN KEY (claim_id) REFERENCES claims(claim_id) ON DELETE CASCADE
);
