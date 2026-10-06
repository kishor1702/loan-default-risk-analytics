-- 04_build_previous_application.sql

DROP TABLE IF EXISTS credit_risk.previous_application;

CREATE TABLE credit_risk.previous_application AS
SELECT
    sk_id_prev::BIGINT AS previous_application_id,
    sk_id_curr::BIGINT AS customer_id,

    name_contract_status AS contract_status,
    NULLIF(amt_application, '')::NUMERIC AS application_amount,
    NULLIF(amt_credit, '')::NUMERIC AS credit_amount,
    NULLIF(amt_annuity, '')::NUMERIC AS annuity_amount,
    NULLIF(amt_goods_price, '')::NUMERIC AS goods_price,
    name_contract_type,
    weekday_appr_process_start,
    NULLIF(hour_appr_process_start, '')::INTEGER
        AS hour_appr_process_start,
    NULLIF(days_decision, '')::INTEGER AS days_decision,
    name_client_type,
    name_product_type

FROM credit_risk_staging.previous_application;

ALTER TABLE credit_risk.previous_application
    ADD PRIMARY KEY (previous_application_id);

CREATE INDEX idx_previous_customer
    ON credit_risk.previous_application(customer_id);
