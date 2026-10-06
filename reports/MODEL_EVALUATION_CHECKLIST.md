# Model Evaluation Checklist

Before presenting model results:

- [ ] Confirm TARGET is not included in features.
- [ ] Confirm identifiers are excluded from predictive features.
- [ ] Confirm post-decision repayment information is not included.
- [ ] Review ROC-AUC, Gini and KS together.
- [ ] Review PR-AUC because default is an imbalanced class.
- [ ] Inspect score deciles.
- [ ] Check recall at the intended review/approval threshold.
- [ ] Compare Logistic Regression with LightGBM.
- [ ] Do not claim causal relationships from feature importance.
- [ ] For production-style modeling, replace the fallback random split with
      an out-of-time split when a reliable application decision date is available.
