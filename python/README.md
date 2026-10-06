# Python

Python is used here after the SQL layer has been validated.

## Scripts

### `01_profile_dataset.py`
Reads the raw CSV files and produces a simple profile:
- row count
- column count
- data types
- missing values
- sample statistics

### `02_load_home_credit.py`
Loads the Home Credit CSV files into PostgreSQL staging tables.

### `02_eda.py`
Looks at:
- target distribution
- missing values
- numeric variables
- credit amount
- external scores
- default rate by selected business dimensions

Charts are saved under `reports/figures/`.

### `03_feature_engineering.py`
Creates model-ready variables such as:
- credit/income ratio
- annuity/income ratio
- age
- employment years
- external-score aggregates
- log-transformed financial variables

### `04_modeling.py`
Builds two models:
- Logistic Regression
- LightGBM

The script reports ROC-AUC, Gini, KS, PR-AUC, precision, recall and confusion matrices.

### `05_shap_business_layer.py`
Uses the trained LightGBM model to:
- rank important features with SHAP
- generate risk bands
- estimate expected loss
- compare different review thresholds
- create a score-decile summary
- create a high-risk loan list

## Why two models?

Logistic Regression gives a simple baseline that is easy to explain.

LightGBM is then used as a stronger tree-based model and compared against the baseline rather than being used without a reference point.
