-- =========================================================
-- RISKGUARD - SQL INTERVIEW DRILLS
-- =========================================================
-- This script contains 15-20 SQL queries intended for 
-- practicing standard technical interview concepts.
-- =========================================================

-- 1. Simple SELECT
-- Retrieve all claims with an amount greater than 5000.
SELECT claim_id, claim_amount, claim_category 
FROM claims 
WHERE claim_amount > 5000;

-- 2. Basic Aggregation (COUNT)
-- Count the total number of claims submitted.
SELECT COUNT(claim_id) AS total_claims 
FROM claims;

-- 3. Basic Aggregation (SUM, AVG)
-- Find the total and average claim amount for all claims.
SELECT SUM(claim_amount) AS total_amount, AVG(claim_amount) AS average_amount 
FROM claims;

-- 4. Basic Aggregation (MIN, MAX)
-- Find the smallest and largest claim amounts.
SELECT MIN(claim_amount) AS min_claim, MAX(claim_amount) AS max_claim 
FROM claims;

-- 5. GROUP BY
-- Find the number of claims submitted per category.
SELECT claim_category, COUNT(claim_id) AS category_count 
FROM claims 
GROUP BY claim_category;

-- 6. GROUP BY with HAVING
-- Find categories that have more than 2 claims submitted.
SELECT claim_category, COUNT(claim_id) AS category_count 
FROM claims 
GROUP BY claim_category 
HAVING COUNT(claim_id) > 2;

-- 7. INNER JOIN
-- Retrieve the claim details along with their computed risk score.
SELECT c.claim_id, c.claim_amount, r.risk_score, r.prediction
FROM claims c
INNER JOIN risk_results r ON c.claim_id = r.claim_id;

-- 8. LEFT JOIN (Handling potentially missing results)
-- Retrieve all claims, and if available, their risk results. 
SELECT c.claim_id, c.claim_amount, r.risk_score
FROM claims c
LEFT JOIN risk_results r ON c.claim_id = r.claim_id;

-- 9. JOIN with Aggregation
-- Find the average risk score per claim category.
SELECT c.claim_category, AVG(r.risk_score) AS avg_risk
FROM claims c
INNER JOIN risk_results r ON c.claim_id = r.claim_id
GROUP BY c.claim_category;

-- 10. JOIN with Filtering (WHERE)
-- Find claims predicted as 'FRAUD' (risk_score >= 0.5) with amounts > 10000.
SELECT c.claim_id, c.claim_amount, r.prediction
FROM claims c
INNER JOIN risk_results r ON c.claim_id = r.claim_id
WHERE r.prediction = 'FRAUD' AND c.claim_amount > 10000;

-- 11. Subquery in WHERE
-- Find all claims that have a claim amount higher than the overall average.
SELECT claim_id, claim_amount 
FROM claims 
WHERE claim_amount > (SELECT AVG(claim_amount) FROM claims);

-- 12. Subquery in SELECT
-- Select the claim ID, amount, and the overall average amount as a separate column.
SELECT claim_id, claim_amount, 
       (SELECT AVG(claim_amount) FROM claims) AS overall_avg
FROM claims;

-- 13. Complex Aggregation with JOIN and HAVING
-- Find categories where the average risk score is considered high (>0.3).
SELECT c.claim_category, COUNT(c.claim_id) AS num_claims, AVG(r.risk_score) AS avg_risk
FROM claims c
INNER JOIN risk_results r ON c.claim_id = r.claim_id
GROUP BY c.claim_category
HAVING AVG(r.risk_score) > 0.3;

-- 14. Ordering and Limiting (Top N)
-- Find the top 3 highest risk claims.
SELECT c.claim_id, c.claim_amount, r.risk_score
FROM claims c
INNER JOIN risk_results r ON c.claim_id = r.claim_id
ORDER BY r.risk_score DESC
LIMIT 3;

-- 15. Aggregation with CASE (Conditional Aggregation)
-- Count how many claims are HOME vs AUTO in a single row.
SELECT 
    SUM(CASE WHEN claim_category = 'HOME' THEN 1 ELSE 0 END) AS home_claims,
    SUM(CASE WHEN claim_category = 'AUTO' THEN 1 ELSE 0 END) AS auto_claims
FROM claims;
