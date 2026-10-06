# Modeling Plan — Loan Default Risk

## Target
`target = 1` represents the default class in the selected Home Credit training data.

## Baseline
Logistic Regression.

## Challenger
LightGBM.

## Validation
Do not use a random split if an application decision date/time is available.
Prefer:
- earlier observations → training
- later observations → out-of-time validation

If the selected data does not provide a reliable temporal split, document
the limitation and use a stratified train/test split as a fallback.

## Metrics
Primary:
- ROC-AUC
- KS
- Gini
- Precision
- Recall

Business metrics:
- recall at selected approval/review cut-off
- score deciles
- expected loss

## Leakage checklist
Before training, verify that:
- TARGET is never used as a feature.
- post-default repayment fields are not used.
- variables created from future transactions are excluded.
- target-derived aggregates are excluded.
- train/test preprocessing is fitted only on training data.

## Expected-loss framework
Expected Loss = PD × LGD × EAD

All LGD assumptions must be explicitly documented because the dataset
does not automatically provide a complete recovery model.
