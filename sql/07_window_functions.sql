-- 07_window_functions.sql
-- Advanced SQL using window functions

-- ============================================================
-- 1. Risk segment ranking
-- Rank segments by default rate within meaningful population sizes.
-- ============================================================
WITH segment AS (
    SELECT
        income_type,
        education_type,
        COUNT(*) AS applications,
        SUM(credit_amount) AS exposure,
        AVG(target::numeric) AS default_rate
    FROM credit_risk.loan_application
    GROUP BY income_type, education_type
    HAVING COUNT(*) >= 500
)
SELECT
    income_type,
    education_type,
    applications,
    exposure,
    ROUND(100.0 * default_rate, 2) AS default_rate_pct,
    RANK() OVER (ORDER BY default_rate DESC) AS risk_rank
FROM segment
ORDER BY risk_rank;


-- ============================================================
-- 2. Exposure share by income type
-- ============================================================
WITH income_summary AS (
    SELECT
        income_type,
        SUM(credit_amount) AS exposure
    FROM credit_risk.loan_application
    GROUP BY income_type
)
SELECT
    income_type,
    exposure,
    ROUND(
        100.0 * exposure / SUM(exposure) OVER (),
        2
    ) AS exposure_share_pct
FROM income_summary
ORDER BY exposure DESC;


-- ============================================================
-- 3. Default rate vs portfolio average
-- ============================================================
WITH segment AS (
    SELECT
        income_type,
        COUNT(*) AS applications,
        AVG(target::numeric) AS default_rate
    FROM credit_risk.loan_application
    GROUP BY income_type
    HAVING COUNT(*) >= 500
)
SELECT
    income_type,
    applications,
    ROUND(100.0 * default_rate, 2) AS segment_default_rate_pct,
    ROUND(
        100.0 * (
            default_rate
            - AVG(default_rate) OVER ()
        ),
        2
    ) AS difference_from_segment_average_pp
FROM segment
ORDER BY difference_from_segment_average_pp DESC;


-- ============================================================
-- 4. Bureau history per customer
-- Rank customers by number of historical bureau records.
-- ============================================================
WITH bureau_summary AS (
    SELECT
        customer_id,
        COUNT(*) AS bureau_accounts,
        SUM(COALESCE(amt_credit_sum_debt, 0)) AS total_bureau_debt,
        AVG(days_credit) AS avg_days_since_credit
    FROM credit_risk.bureau_credit
    GROUP BY customer_id
)
SELECT
    customer_id,
    bureau_accounts,
    total_bureau_debt,
    RANK() OVER (
        ORDER BY bureau_accounts DESC
    ) AS bureau_history_rank
FROM bureau_summary
ORDER BY bureau_history_rank
LIMIT 100;


-- ============================================================
-- 5. Previous application status mix
-- ============================================================
WITH status_summary AS (
    SELECT
        customer_id,
        COUNT(*) AS previous_applications,
        COUNT(*) FILTER (
            WHERE UPPER(contract_status) = 'APPROVED'
        ) AS approved_count,
        COUNT(*) FILTER (
            WHERE UPPER(contract_status) = 'REFUSED'
        ) AS refused_count
    FROM credit_risk.previous_application
    GROUP BY customer_id
)
SELECT
    customer_id,
    previous_applications,
    approved_count,
    refused_count,
    ROUND(
        100.0 * approved_count / NULLIF(previous_applications, 0),
        2
    ) AS approval_rate_pct,
    NTILE(10) OVER (
        ORDER BY previous_applications DESC
    ) AS activity_decile
FROM status_summary
ORDER BY previous_applications DESC;
