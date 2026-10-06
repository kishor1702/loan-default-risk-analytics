-- Portfolio Risk Analysis

-- 1. Overall portfolio
SELECT
    COUNT(*) AS applications,
    SUM(credit_amount) AS total_credit_exposure,
    AVG(credit_amount) AS avg_credit,
    AVG(target::numeric) AS default_rate
FROM credit_risk.loan_application;

-- 2. Income bands
WITH bands AS (
    SELECT *,
        CASE
            WHEN income_amount < 100000 THEN '<100K'
            WHEN income_amount < 200000 THEN '100K-200K'
            WHEN income_amount < 500000 THEN '200K-500K'
            ELSE '500K+'
        END AS income_band
    FROM credit_risk.loan_application
)
SELECT
    income_band,
    COUNT(*) AS applications,
    SUM(credit_amount) AS exposure,
    ROUND(100.0 * AVG(target::numeric), 2) AS default_rate_pct
FROM bands
GROUP BY income_band
ORDER BY default_rate_pct DESC;

-- 3. Credit-to-income ratio
SELECT
    CASE
        WHEN income_amount = 0 THEN 'Unknown'
        WHEN credit_amount / income_amount < 2 THEN '<2x'
        WHEN credit_amount / income_amount < 4 THEN '2x-4x'
        ELSE '4x+'
    END AS debt_to_income_band,
    COUNT(*) AS applications,
    ROUND(100.0 * AVG(target::numeric), 2) AS default_rate_pct
FROM credit_risk.loan_application
GROUP BY 1
ORDER BY default_rate_pct DESC;
