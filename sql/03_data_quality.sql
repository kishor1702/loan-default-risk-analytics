-- Data Quality Checks

-- 1. Duplicate current loan IDs
SELECT loan_id, COUNT(*)
FROM credit_risk.loan_application
GROUP BY loan_id
HAVING COUNT(*) > 1;

-- 2. Missing critical fields
SELECT
    COUNT(*) FILTER (WHERE customer_id IS NULL) AS missing_customer,
    COUNT(*) FILTER (WHERE income_amount IS NULL) AS missing_income,
    COUNT(*) FILTER (WHERE credit_amount IS NULL) AS missing_credit,
    COUNT(*) FILTER (WHERE target IS NULL) AS missing_target
FROM credit_risk.loan_application;

-- 3. Invalid monetary values
SELECT COUNT(*) AS invalid_amounts
FROM credit_risk.loan_application
WHERE income_amount < 0
   OR credit_amount < 0
   OR annuity_amount < 0
   OR goods_price < 0;

-- 4. Target distribution
SELECT target, COUNT(*) AS applications
FROM credit_risk.loan_application
GROUP BY target
ORDER BY target;

-- 5. Basic outlier scan
SELECT
    MIN(income_amount) AS min_income,
    MAX(income_amount) AS max_income,
    MIN(credit_amount) AS min_credit,
    MAX(credit_amount) AS max_credit
FROM credit_risk.loan_application;
