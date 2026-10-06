-- Project: Loan Default Risk Analytics
-- PostgreSQL schema
-- Run this script before loading CSV data.

CREATE SCHEMA IF NOT EXISTS credit_risk;

CREATE TABLE IF NOT EXISTS credit_risk.customer (
    customer_id BIGINT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS credit_risk.loan_application (
    loan_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES credit_risk.customer(customer_id),
    contract_type VARCHAR(50),
    gender VARCHAR(20),
    owns_car BOOLEAN,
    owns_realty BOOLEAN,
    income_type VARCHAR(100),
    education_type VARCHAR(100),
    family_status VARCHAR(100),
    occupation_type VARCHAR(100),
    organization_type VARCHAR(100),
    income_amount NUMERIC(18,2),
    credit_amount NUMERIC(18,2),
    annuity_amount NUMERIC(18,2),
    goods_price NUMERIC(18,2),
    days_birth INTEGER,
    days_employed INTEGER,
    region_population_relative NUMERIC(18,6),
    ext_source_1 NUMERIC(18,8),
    ext_source_2 NUMERIC(18,8),
    ext_source_3 NUMERIC(18,8),
    target SMALLINT CHECK (target IN (0,1))
);

CREATE TABLE IF NOT EXISTS credit_risk.bureau_credit (
    bureau_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES credit_risk.customer(customer_id),
    credit_active VARCHAR(50),
    credit_currency VARCHAR(50),
    credit_type VARCHAR(100),
    days_credit INTEGER,
    days_credit_enddate NUMERIC(18,2),
    days_enddate_fact NUMERIC(18,2),
    amt_credit_max_overdue NUMERIC(18,2),
    amt_credit_sum NUMERIC(18,2),
    amt_credit_sum_debt NUMERIC(18,2),
    amt_credit_sum_limit NUMERIC(18,2),
    amt_annuity NUMERIC(18,2)
);

CREATE TABLE IF NOT EXISTS credit_risk.previous_application (
    previous_application_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES credit_risk.customer(customer_id),
    contract_status VARCHAR(50),
    application_amount NUMERIC(18,2),
    credit_amount NUMERIC(18,2),
    annuity_amount NUMERIC(18,2),
    goods_price NUMERIC(18,2),
    name_contract_type VARCHAR(100),
    weekday_appr_process_start VARCHAR(30),
    hour_appr_process_start INTEGER,
    days_decision INTEGER,
    name_client_type VARCHAR(100),
    name_product_type VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_loan_customer
    ON credit_risk.loan_application(customer_id);

CREATE INDEX IF NOT EXISTS idx_bureau_customer
    ON credit_risk.bureau_credit(customer_id);

CREATE INDEX IF NOT EXISTS idx_previous_customer
    ON credit_risk.previous_application(customer_id);

COMMENT ON TABLE credit_risk.loan_application IS
'One row per current Home Credit loan application. TARGET=1 indicates default in the source competition.';
