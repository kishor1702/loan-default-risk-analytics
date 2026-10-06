-- Power BI curated SQL layer
DROP VIEW IF EXISTS credit_risk.vw_powerbi_portfolio;
CREATE VIEW credit_risk.vw_powerbi_portfolio AS
SELECT loan_id, customer_id, contract_type, income_type, education_type,
       family_status, occupation_type, gender, region_rating,
       credit_amount, annuity_amount, income_amount,
       external_score_1, external_score_2, external_score_3, target,
       CASE WHEN target=1 THEN 'Default' ELSE 'Non-Default' END AS default_status,
       CASE
         WHEN income_amount IS NULL OR income_amount<=0 THEN 'Unknown'
         WHEN income_amount<100000 THEN '<100K'
         WHEN income_amount<250000 THEN '100K-250K'
         WHEN income_amount<500000 THEN '250K-500K'
         WHEN income_amount<1000000 THEN '500K-1M'
         ELSE '1M+'
       END AS income_band,
       CASE
         WHEN external_score_2 IS NULL THEN 'Missing'
         WHEN external_score_2<0.30 THEN '<0.30'
         WHEN external_score_2<0.50 THEN '0.30-0.50'
         WHEN external_score_2<0.70 THEN '0.50-0.70'
         ELSE '0.70+'
       END AS ext_score_2_band
FROM credit_risk.loan_application;

DROP VIEW IF EXISTS credit_risk.vw_powerbi_risk_segments;
CREATE VIEW credit_risk.vw_powerbi_risk_segments AS
SELECT loan_id, customer_id, contract_type, income_type, education_type,
       occupation_type, region_rating, credit_amount, income_amount,
       external_score_1, external_score_2, external_score_3, target,
       CASE
         WHEN external_score_2 IS NULL THEN 'Score Missing'
         WHEN external_score_2<0.30 THEN 'Very Low Score'
         WHEN external_score_2<0.50 THEN 'Low Score'
         WHEN external_score_2<0.70 THEN 'Medium Score'
         ELSE 'High Score'
       END AS score_segment,
       CASE
         WHEN income_amount IS NULL OR income_amount<=0 THEN 'Unknown'
         WHEN credit_amount/NULLIF(income_amount,0)>=5 THEN 'Very High Leverage'
         WHEN credit_amount/NULLIF(income_amount,0)>=3 THEN 'High Leverage'
         WHEN credit_amount/NULLIF(income_amount,0)>=1.5 THEN 'Medium Leverage'
         ELSE 'Low Leverage'
       END AS leverage_segment
FROM credit_risk.loan_application;

DROP TABLE IF EXISTS credit_risk.powerbi_model_scores;
CREATE TABLE credit_risk.powerbi_model_scores (
    loan_id BIGINT, customer_id BIGINT, target INTEGER,
    predicted_pd DOUBLE PRECISION, risk_band TEXT,
    ead DOUBLE PRECISION, expected_loss DOUBLE PRECISION,
    scoring_date DATE DEFAULT CURRENT_DATE
);
