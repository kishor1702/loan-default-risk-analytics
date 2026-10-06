-- 10_previous_application_analysis.sql

WITH customer_history AS (
    SELECT
        customer_id,

        COUNT(*) AS previous_application_count,

        COUNT(*) FILTER (
            WHERE UPPER(contract_status) = 'APPROVED'
        ) AS approved_count,

        COUNT(*) FILTER (
            WHERE UPPER(contract_status) = 'REFUSED'
        ) AS refused_count,

        AVG(credit_amount) AS avg_previous_credit,

        SUM(
            CASE
                WHEN UPPER(contract_status) = 'APPROVED'
                THEN COALESCE(credit_amount, 0)
                ELSE 0
            END
        ) AS approved_credit_amount

    FROM credit_risk.previous_application
    GROUP BY customer_id
)
SELECT
    customer_id,
    previous_application_count,
    approved_count,
    refused_count,

    ROUND(
        100.0 * approved_count
        / NULLIF(previous_application_count, 0),
        2
    ) AS approval_rate_pct,

    avg_previous_credit,
    approved_credit_amount

FROM customer_history
ORDER BY previous_application_count DESC;
