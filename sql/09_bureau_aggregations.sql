-- 09_bureau_aggregations.sql
-- Aggregate historical bureau information to customer level.
-- These features will later be joined to the current application table.

WITH bureau_customer AS (
    SELECT
        customer_id,
        COUNT(*) AS bureau_account_count,

        COUNT(*) FILTER (
            WHERE UPPER(credit_active) = 'ACTIVE'
        ) AS active_bureau_accounts,

        SUM(COALESCE(amt_credit_sum, 0)) AS total_bureau_credit,

        SUM(COALESCE(amt_credit_sum_debt, 0)) AS total_bureau_debt,

        AVG(days_credit) AS avg_days_credit,

        MAX(days_credit) AS max_days_credit

    FROM credit_risk.bureau_credit
    GROUP BY customer_id
)
SELECT
    customer_id,
    bureau_account_count,
    active_bureau_accounts,
    total_bureau_credit,
    total_bureau_debt,
    avg_days_credit,
    max_days_credit
FROM bureau_customer
ORDER BY total_bureau_debt DESC
LIMIT 100;
