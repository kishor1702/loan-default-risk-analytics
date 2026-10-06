# Source-to-Analytics Mapping

Reference mapping — complete with the actual source profile when running the project. `python/01_profile_dataset.py`.

| Analytics field | Source file | Source column | Transformation | Leakage check |
|---|---|---|---|---|
| customer_id | | | | |
| loan_id | | | | |
| income_amount | | | | |
| credit_amount | | | | |
| annuity_amount | | | | |
| education_type | | | | |
| occupation_type | | | | |
| target | | | | |
| application_date | | | | |

## Rules

1. Use only columns that are available at the relevant decision point for
   predictive modeling.
2. Historical bureau/application information must be aggregated using a
   clearly defined time window where necessary.
3. Any feature created using the target or post-decision repayment outcome
   must be excluded from the model.
4. Record every transformation and assumption.
