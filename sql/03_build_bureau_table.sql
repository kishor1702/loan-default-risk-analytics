-- 03_build_bureau_table.sql

DROP TABLE IF EXISTS credit_risk.bureau_credit;

CREATE TABLE credit_risk.bureau_credit AS
SELECT
    sk_id_bureau::BIGINT AS bureau_id,
    sk_id_curr::BIGINT AS customer_id,

    credit_active,
    credit_currency,
    credit_type,

    NULLIF(days_credit, '')::INTEGER AS days_credit,
    NULLIF(days_credit_enddate, '')::NUMERIC AS days_credit_enddate,
    NULLIF(days_enddate_fact, '')::NUMERIC AS days_enddate_fact,
    NULLIF(amt_credit_max_overdue, '')::NUMERIC AS amt_credit_max_overdue,
    NULLIF(amt_credit_sum, '')::NUMERIC AS amt_credit_sum,
    NULLIF(amt_credit_sum_debt, '')::NUMERIC AS amt_credit_sum_debt,
    NULLIF(amt_credit_sum_limit, '')::NUMERIC AS amt_credit_sum_limit,
    NULLIF(amt_annuity, '')::NUMERIC AS amt_annuity

FROM credit_risk_staging.bureau;

ALTER TABLE credit_risk.bureau_credit
    ADD PRIMARY KEY (bureau_id);

CREATE INDEX idx_bureau_customer
    ON credit_risk.bureau_credit(customer_id);
