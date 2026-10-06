# Power BI Data Dictionary

| Field | Meaning | Use |
|---|---|---|
| loan_id | Loan/application identifier | Detail |
| customer_id | Customer identifier | Detail |
| contract_type | Loan product/contract | Segmentation |
| income_type | Income/employment type | Risk |
| education_type | Education category | Risk |
| occupation_type | Occupation category | Risk |
| region_rating | Region rating | Risk |
| credit_amount | Credit exposure | Exposure/EAD proxy |
| income_amount | Customer income | Affordability |
| external_score_1/2/3 | External risk scores | Risk |
| target | Observed default indicator | Default rate |
| predicted_pd | Model probability of default | Model |
| risk_band | Model risk category | Monitoring |
| ead | Exposure at default proxy | Expected loss |
| expected_loss | PD × LGD × EAD | Prioritization |
