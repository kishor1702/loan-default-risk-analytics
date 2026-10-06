-- 08_customer_risk_segments.sql
-- Multi-dimensional risk segmentation

WITH base AS (
    SELECT
        loan_id,
        customer_id,
        credit_amount,
        income_amount,
        target,
        ext_source_1,
        ext_source_2,
        ext_source_3,

        CASE
            WHEN income_amount IS NULL OR income_amount = 0
                THEN 'Unknown'
            WHEN credit_amount / income_amount < 2
                THEN 'Low leverage'
            WHEN credit_amount / income_amount < 4
                THEN 'Medium leverage'
            ELSE 'High leverage'
        END AS leverage_segment,

        CASE
            WHEN COALESCE(ext_source_2, 0) >= 0.70
                THEN 'Strong external score'
            WHEN COALESCE(ext_source_2, 0) >= 0.40
                THEN 'Medium external score'
            WHEN ext_source_2 IS NULL
                THEN 'Missing external score'
            ELSE 'Weak external score'
        END AS score_segment
    FROM credit_risk.loan_application
),
segments AS (
    SELECT
        leverage_segment,
        score_segment,
        COUNT(*) AS applications,
        SUM(credit_amount) AS exposure,
        SUM(target) AS defaults,
        AVG(target::numeric) AS default_rate
    FROM base
    GROUP BY leverage_segment, score_segment
    HAVING COUNT(*) >= 250
)
SELECT
    leverage_segment,
    score_segment,
    applications,
    exposure,
    defaults,
    ROUND(100.0 * default_rate, 2) AS default_rate_pct,
    RANK() OVER (
        ORDER BY default_rate DESC, exposure DESC
    ) AS risk_rank
FROM segments
ORDER BY risk_rank;


-- High-risk / high-exposure segments
WITH segments AS (
    SELECT
        CASE
            WHEN income_amount IS NULL OR income_amount = 0
                THEN 'Unknown'
            WHEN credit_amount / income_amount < 2
                THEN 'Low leverage'
            WHEN credit_amount / income_amount < 4
                THEN 'Medium leverage'
            ELSE 'High leverage'
        END AS leverage_segment,

        CASE
            WHEN COALESCE(ext_source_2, 0) >= 0.70
                THEN 'Strong external score'
            WHEN COALESCE(ext_source_2, 0) >= 0.40
                THEN 'Medium external score'
            WHEN ext_source_2 IS NULL
                THEN 'Missing external score'
            ELSE 'Weak external score'
        END AS score_segment,

        credit_amount,
        target
    FROM credit_risk.loan_application
)
SELECT
    leverage_segment,
    score_segment,
    COUNT(*) AS applications,
    SUM(credit_amount) AS exposure,
    ROUND(100.0 * AVG(target::numeric), 2) AS default_rate_pct
FROM segments
GROUP BY leverage_segment, score_segment
HAVING COUNT(*) >= 250
ORDER BY default_rate_pct DESC, exposure DESC;
