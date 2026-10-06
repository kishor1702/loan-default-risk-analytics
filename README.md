# Loan Default Risk Analysis

A practical credit-risk analytics project built using **PostgreSQL, Python and Power BI**.

I built this project to answer a simple business question:

> **Which loan/customer segments show higher default risk, and how can the analysis help a lending team prioritise risk?**

The project starts with raw lending data, uses SQL for portfolio analysis, Python for modelling and explanation, and Power BI for presenting the results.

---

## What I worked on

### 1. SQL
- Loaded and organised the source data in PostgreSQL
- Checked missing values and data quality
- Calculated portfolio-level KPIs
- Compared default rates across customer segments
- Used CTEs, joins and window functions
- Built risk segments using income, credit exposure and external scores
- Aggregated historical bureau and previous-application information

### 2. Python
- Profiled the dataset
- Performed exploratory analysis
- Created features such as:
  - Credit-to-income ratio
  - Annuity-to-income ratio
  - Age and employment features
  - External-score summaries
  - Log-transformed financial variables
- Trained:
  - Logistic Regression
  - LightGBM
- Evaluated the models using ROC-AUC, Gini, KS and PR-AUC
- Used SHAP to understand the main drivers behind predictions
- Converted model scores into practical risk bands

### 3. Business risk view
For portfolio prioritisation, I created:
- Predicted probability of default
- Low / Medium / High / Very High risk bands
- Expected-loss estimate using `PD × LGD × EAD`
- Threshold analysis
- Score-decile analysis
- A high-risk loan list

> The LGD value used for the expected-loss example is an illustrative assumption. It is not a lender policy or an observed company value.

### 4. Power BI
The Power BI layer is designed around five pages:

1. **Portfolio Overview**
2. **Risk Segmentation**
3. **Model Performance**
4. **High-Risk Loan List**
5. **Executive Insights**

---

## Project flow

```text
Raw CSV files
     |
     v
PostgreSQL
     |
     +---- SQL analysis
     |       |
     |       +-- Portfolio KPIs
     |       +-- Default analysis
     |       +-- Risk segments
     |
     v
Python
     |
     +-- EDA
     +-- Feature engineering
     +-- Logistic Regression
     +-- LightGBM
     +-- SHAP
     |
     v
Risk scoring
     |
     +-- PD
     +-- Risk band
     +-- Expected loss
     |
     v
Power BI
     |
     +-- Portfolio
     +-- Risk segments
     +-- Model performance
     +-- High-risk loans
```

---

## Repository structure

```text
loan-default-risk-analytics/
│
├── data/
│   ├── raw/                  # Source files - not committed
│   └── processed/            # Generated analysis files
│
├── sql/
│   ├── 01_create_schema.sql
│   ├── 02_build_core_tables.sql
│   ├── 03_build_bureau_table.sql
│   ├── 04_build_previous_application.sql
│   ├── 05_validate_core_tables.sql
│   ├── 06_core_risk_analysis.sql
│   ├── 07_window_functions.sql
│   ├── 08_customer_risk_segments.sql
│   ├── 09_bureau_aggregations.sql
│   └── 10_previous_application_analysis.sql
│
├── python/
│   ├── 01_profile_dataset.py
│   ├── 02_load_home_credit.py
│   ├── 02_eda.py
│   ├── 03_feature_engineering.py
│   ├── 04_modeling.py
│   └── 05_shap_business_layer.py
│
├── powerbi/
│   ├── 01_powerbi_views.sql
│   ├── 02_dax_measures.txt
│   ├── 03_dashboard_build_guide.md
│   └── 04_data_dictionary.md
│
├── reports/
├── models/
├── requirements.txt
└── README.md
```

---

## Dataset

The project uses the **Home Credit Default Risk** dataset.

The source files are intentionally not included in this repository because they are large. Download the dataset separately and place the required CSV files under:

```text
data/raw/
```

The main files used by the project are:

- `application_train.csv`
- `bureau.csv`
- `previous_application.csv`
- `installments_payments.csv`

---

## How to run

### PostgreSQL

Create a database and configure the connection through environment variables:

```text
PGHOST
PGPORT
PGDATABASE
PGUSER
PGPASSWORD
```

Then run the SQL scripts in sequence.

### Python

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the main stages:

```bash
python python/01_profile_dataset.py
python python/02_eda.py
python python/03_feature_engineering.py
python python/04_modeling.py
python python/05_shap_business_layer.py
```

### Power BI

Open Power BI Desktop and connect to the PostgreSQL views described in:

```text
powerbi/01_powerbi_views.sql
```

The DAX measures and dashboard layout are documented in the `powerbi/` folder.

---

## A few things I paid attention to

### Leakage

I did not use post-loan repayment information as a predictive feature.

Historical information needs to be aggregated using an appropriate time window so that the model only sees information that would have been available at the relevant decision point.

### Imbalanced target

Default cases are much less frequent than non-default cases, so model evaluation should not rely only on accuracy. This is why the project focuses on ROC-AUC, Gini, KS, PR-AUC, precision and recall.

### Model validation

The current modelling script uses a stratified train/test split because a reliable decision-date field has not yet been validated for an out-of-time split.

For a production credit-risk model, I would use an out-of-time validation strategy once the correct decision date is confirmed.

---

## What I would improve next

If I were taking this project further, I would add:

- Out-of-time validation
- Model calibration
- Population Stability Index (PSI)
- More robust bureau-history features
- Threshold selection based on an agreed business cost
- A proper Power BI `.pbix` report with refreshed model scores
- Monitoring for model drift

---

## Tools used

**SQL:** PostgreSQL  
**Python:** Pandas, NumPy, Scikit-learn, LightGBM, SHAP, Matplotlib  
**BI:** Power BI, DAX  
**Version control:** Git / GitHub

---

## Note

This is a portfolio project built for learning and demonstrating practical analytics skills. It should not be treated as a production lending or underwriting model.
