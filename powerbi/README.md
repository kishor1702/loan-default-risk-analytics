# Power BI

This folder contains the Power BI layer for the loan-risk project.

The dashboard is designed to answer business questions rather than simply display charts.

## Dashboard pages

### 01 — Portfolio Overview
A quick view of the portfolio:
- Total loans
- Credit exposure
- Default rate
- Defaulted loans
- Average loan amount
- Default rate by customer segment

### 02 — Risk Segmentation
Focuses on combinations of:
- External score
- Credit-to-income leverage
- Income type
- Occupation
- Region

The main view is a score × leverage matrix so that high-risk combinations are easy to spot.

### 03 — Model Performance
Shows:
- Average predicted PD
- High-risk loan count
- High-risk exposure
- Expected loss
- Actual default rate by score decile
- Risk band performance

### 04 — High-Risk Loan List
A practical table for reviewing individual loans:

`Loan ID | Customer ID | PD | Risk Band | EAD | Expected Loss`

Sort by expected loss to prioritise the largest potential exposure.

### 05 — Executive Insights
A small set of business-focused observations:
- Where default risk is highest
- Where exposure is concentrated
- Which risk bands contribute most to expected loss
- How much of the portfolio falls into high-risk categories

## Files

- `01_powerbi_views.sql` — SQL views used as Power BI sources
- `02_dax_measures.txt` — core measures
- `03_dashboard_build_guide.md` — visual/page instructions
- `04_data_dictionary.md` — field definitions

The repository contains the Power BI preparation layer. The actual `.pbix` file should be created in Power BI Desktop after the PostgreSQL data connection is configured.
