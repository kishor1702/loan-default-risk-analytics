-- 02_build_core_tables.sql
-- Convert selected Home Credit staging columns into typed analytical tables.
--
-- Source names are normalized to lowercase by the loader.
-- Home Credit's main application table uses SK_ID_CURR as the customer/
-- application identifier and TARGET as the default target.

DROP TABLE IF EXISTS credit_risk.loan_application;

CREATE TABLE credit_risk.loan_application AS
SELECT
    sk_id_curr::BIGINT AS loan_id,
    sk_id_curr::BIGINT AS customer_id,

    name_contract_type AS contract_type,
    code_gender AS gender,

    CASE
        WHEN flag_own_car = '1' THEN TRUE
        WHEN flag_own_car = '0' THEN FALSE
        ELSE NULL
    END AS owns_car,

    CASE
        WHEN flag_own_realty = '1' THEN TRUE
        WHEN flag_own_realty = '0' THEN FALSE
        ELSE NULL
    END AS owns_realty,

    name_income_type AS income_type,
    name_education_type AS education_type,
    name_family_status AS family_status,
    occupation_type,
    organization_type,

    NULLIF(amt_income_total, '')::NUMERIC AS income_amount,
    NULLIF(amt_credit, '')::NUMERIC AS credit_amount,
    NULLIF(amt_annuity, '')::NUMERIC AS annuity_amount,
    NULLIF(amt_goods_price, '')::NUMERIC AS goods_price,

    NULLIF(days_birth, '')::INTEGER AS days_birth,
    NULLIF(days_employed, '')::INTEGER AS days_employed,

    NULLIF(region_population_relative, '')::NUMERIC
        AS region_population_relative,

    NULLIF(ext_source_1, '')::NUMERIC AS ext_source_1,
    NULLIF(ext_source_2, '')::NUMERIC AS ext_source_2,
    NULLIF(ext_source_3, '')::NUMERIC AS ext_source_3,

    NULLIF(target, '')::SMALLINT AS target

FROM credit_risk_staging.application_train;

ALTER TABLE credit_risk.loan_application
    ADD PRIMARY KEY (loan_id);

CREATE INDEX idx_loan_application_customer
    ON credit_risk.loan_application(customer_id);
