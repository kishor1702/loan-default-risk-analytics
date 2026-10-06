-- 05_validate_core_tables.sql

-- Row counts
SELECT 'loan_application' AS table_name, COUNT(*) AS rows
FROM credit_risk.loan_application
UNION ALL
SELECT 'bureau_credit', COUNT(*)
FROM credit_risk.bureau_credit
UNION ALL
SELECT 'previous_application', COUNT(*)
FROM credit_risk.previous_application;

-- Target distribution
SELECT
    target,
    COUNT(*) AS applications,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM credit_risk.loan_application
GROUP BY target
ORDER BY target;

-- Missingness in core fields
SELECT
    COUNT(*) FILTER (WHERE customer_id IS NULL) AS missing_customer_id,
    COUNT(*) FILTER (WHERE income_amount IS NULL) AS missing_income,
    COUNT(*) FILTER (WHERE credit_amount IS NULL) AS missing_credit,
    COUNT(*) FILTER (WHERE target IS NULL) AS missing_target
FROM credit_risk.loan_application;

-- Basic relationship check
SELECT COUNT(*) AS bureau_rows_without_customer
FROM credit_risk.bureau_credit b
LEFT JOIN credit_risk.loan_application l
    ON b.customer_id = l.customer_id
WHERE l.customer_id IS NULL;
