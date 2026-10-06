# Step 8 — Power BI Dashboard Build Guide

## Pages

### 1. Portfolio Overview
KPI cards: Total Loans, Credit Exposure, Default Rate, Defaulted Loans, Average Loan Amount.
Visuals: Default Rate by Contract Type, Income Type, Education, Region Rating, and Income Band.
Slicers: Contract Type, Income Type, Education, Region Rating, Gender.

### 2. Risk Segmentation
Show Default Rate by Score Segment, Default Rate by Leverage Segment, Score × Leverage matrix, risk concentration and exposure.

### 3. Model Performance
KPI cards: Average Predicted PD, High Risk Loans, High Risk %, Expected Loss, Expected Loss Rate.
Visuals: PD distribution, Actual Default Rate by Score Decile, Risk Band vs Actual Default Rate, Expected Loss by Risk Band.

### 4. High-Risk Loan List
Table: Loan ID, Customer ID, Predicted PD, Risk Band, EAD, Expected Loss, Target.
Sort by Expected Loss descending.

### 5. Executive Insights
Use dynamic cards to answer:
- Which segment has the highest default rate?
- Which risk band has the largest exposure?
- Where is expected loss concentrated?
- What percentage is high risk?

## Model flow

SQL → Python EDA → Feature Engineering → Logistic Regression → LightGBM → SHAP → Risk Scoring → Power BI

## Important limitation

Current model validation uses a stratified train/test split because a reliable decision-date field has not yet been validated for an out-of-time split. LGD used for expected loss is illustrative.
