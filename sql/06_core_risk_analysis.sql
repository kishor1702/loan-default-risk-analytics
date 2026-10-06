-- 06_core_risk_analysis.sql
-- Loan Default Risk Analytics
-- Core portfolio and risk analysis

-- ============================================================
-- 1. Portfolio KPI
-- ============================================================
SELECT
    COUNT(*) AS total_applications,
    SUM(credit_amount) AS total_exposure,
    AVG(credit_amount) AS avg_credit_amount,
    SUM(CASE WHEN target = 1 THEN 1 ELSE 0 END) AS defaulted_applications,
    ROUND(100.0 * AVG(target::numeric), 2) AS default_rate_pct
FROM credit_risk.loan_application;


-- ============================================================
-- 2. Default rate by contract type
-- ============================================================
SELECT
    contract_type,
    COUNT(*) AS applications,
    SUM(credit_amount) AS exposure,
    SUM(CASE WHEN target = 1 THEN 1 ELSE 0 END) AS defaults,
    ROUND(100.0 * AVG(target::numeric), 2) AS default_rate_pct
FROM credit_risk.loan_application
GROUP BY contract_type
ORDER BY default_rate_pct DESC;


-- ============================================================
-- 3. Default rate by income type
-- ============================================================
SELECT
    income_type,
    COUNT(*) AS applications,
    SUM(credit_amount) AS exposure,
    ROUND(100.0 * AVG(target::numeric), 2) AS default_rate_pct
FROM credit_risk.loan_application
GROUP BY income_type
HAVING COUNT(*) >= 100
ORDER BY default_rate_pct DESC;


-- ============================================================
-- 4. Default rate by education
-- ============================================================
SELECT
    education_type,
    COUNT(*) AS applications,
    ROUND(100.0 * AVG(target::numeric), 2) AS default_rate_pct
FROM credit_risk.loan_application
GROUP BY education_type
ORDER BY default_rate_pct DESC;


-- ============================================================
-- 5. Credit-to-income risk bands
-- ============================================================
WITH base AS (
    SELECT
        loan_id,
        credit_amount,
        income_amount,
        target,
        CASE
            WHEN income_amount IS NULL OR income_amount = 0
                THEN 'Unknown'
            WHEN credit_amount / income_amount < 1
                THEN '<1x'
            WHEN credit_amount / income_amount < 2
                THEN '1x-2x'
            WHEN credit_amount / income_amount < 4
                THEN '2x-4x'
            ELSE '4x+'
        END AS credit_income_band
    FROM credit_risk.loan_application
)
SELECT
    credit_income_band,
    COUNT(*) AS applications,
    SUM(credit_amount) AS exposure,
    ROUND(100.0 * AVG(target::numeric), 2) AS default_rate_pct
FROM base
GROUP BY credit_income_band
ORDER BY default_rate_pct DESC;


-- ============================================================
-- 6. External score bands
-- ============================================================
WITH base AS (
    SELECT
        loan_id,
        target,
        ext_source_2,
        CASE
            WHEN ext_source_2 IS NULL THEN 'Unknown'
            WHEN ext_source_2 < 0.20 THEN '<0.20'
            WHEN ext_source_2 < 0.40 THEN '0.20-0.40'
            WHEN ext_source_2 < 0.60 THEN '0.40-0.60'
            WHEN ext_source_2 < 0.80 THEN '0.60-0.80'
            ELSE '0.80+'
        END AS score_band
    FROM credit_risk.loan_application
)
SELECT
    score_band,
    COUNT(*) AS applications,
    ROUND(100.0 * AVG(target::numeric), 2) AS default_rate_pct
FROM base
GROUP BY score_band
ORDER BY default_rate_pct DESC;


-- ============================================================
-- 7. Age bands
-- days_birth is negative in the source.
-- ============================================================
WITH base AS (
    SELECT
        loan_id,
        target,
        FLOOR(ABS(days_birth) / 365.25) AS age_years
    FROM credit_risk.loan_application
)
SELECT
    CASE
        WHEN age_years < 25 THEN '<25'
        WHEN age_years < 35 THEN '25-34'
        WHEN age_years < 45 THEN '35-44'
        WHEN age_years < 55 THEN '45-54'
        ELSE '55+'
    END AS age_band,
    COUNT(*) AS applications,
    ROUND(100.0 * AVG(target::numeric), 2) AS default_rate_pct
FROM base
GROUP BY 1
ORDER BY default_rate_pct DESC;


-- ============================================================
-- 8. Occupation risk
-- Ignore very small groups to avoid unstable rates.
-- ============================================================
SELECT
    COALESCE(occupation_type, 'Unknown') AS occupation_type,
    COUNT(*) AS applications,
    SUM(credit_amount) AS exposure,
    ROUND(100.0 * AVG(target::numeric), 2) AS default_rate_pct
FROM credit_risk.loan_application
GROUP BY COALESCE(occupation_type, 'Unknown')
HAVING COUNT(*) >= 500
ORDER BY default_rate_pct DESC;
