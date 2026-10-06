"""
04_modeling.py
Loan Default Risk Analytics — baseline + challenger models

Models:
1. Logistic Regression with preprocessing
2. LightGBM with preprocessing

Validation:
- Uses a stratified train/test split as a practical fallback when the
  source data does not provide a reliable decision-date field in the
  current analytical table.
- This limitation is documented in 04_modeling_plan.md.

Metrics:
- ROC-AUC
- Gini
- KS
- Precision
- Recall
- PR-AUC

Outputs:
- reports/model_metrics.csv
- reports/model_predictions.csv
- reports/score_deciles.csv
- models/*.joblib
"""

from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    confusion_matrix,
)
from lightgbm import LGBMClassifier

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "loan_features.csv"
REPORTS = ROOT / "reports"
MODELS = ROOT / "models"

REPORTS.mkdir(parents=True, exist_ok=True)
MODELS.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42


def ks_statistic(y_true, probabilities):
    """Maximum separation between cumulative good/bad distributions."""
    tmp = pd.DataFrame({
        "y": np.asarray(y_true),
        "p": np.asarray(probabilities),
    }).sort_values("p", ascending=False)

    total_bad = (tmp["y"] == 1).sum()
    total_good = (tmp["y"] == 0).sum()

    if total_bad == 0 or total_good == 0:
        return np.nan

    tmp["cum_bad"] = (tmp["y"] == 1).cumsum() / total_bad
    tmp["cum_good"] = (tmp["y"] == 0).cumsum() / total_good

    return float((tmp["cum_bad"] - tmp["cum_good"]).abs().max())


def make_deciles(y_true, probabilities):
    df = pd.DataFrame({
        "target": y_true,
        "probability": probabilities
    })

    # Higher probability = higher-risk decile.
    df["risk_decile"] = pd.qcut(
        df["probability"].rank(method="first"),
        q=10,
        labels=False
    ) + 1

    result = (
        df.groupby("risk_decile", as_index=False)
          .agg(
              applications=("target", "size"),
              defaults=("target", "sum"),
              avg_probability=("probability", "mean")
          )
    )

    result["default_rate_pct"] = (
        100 * result["defaults"] / result["applications"]
    )

    result["cumulative_defaults_pct"] = (
        100 * result["defaults"].cumsum()
        / result["defaults"].sum()
    )

    return result


def evaluate_model(name, model, X_test, y_test):
    probability = model.predict_proba(X_test)[:, 1]
    prediction = (probability >= 0.50).astype(int)

    auc = roc_auc_score(y_test, probability)

    metrics = {
        "model": name,
        "roc_auc": auc,
        "gini": 2 * auc - 1,
        "ks": ks_statistic(y_test, probability),
        "pr_auc": average_precision_score(y_test, probability),
        "precision_at_0_50": precision_score(
            y_test, prediction, zero_division=0
        ),
        "recall_at_0_50": recall_score(
            y_test, prediction, zero_division=0
        ),
    }

    return metrics, probability, prediction


def main():
    if not DATA.exists():
        raise FileNotFoundError(
            f"{DATA} not found. Run python/03_feature_engineering.py first."
        )

    df = pd.read_csv(DATA)

    if "target" not in df.columns:
        raise ValueError("target column not found.")

    # Target is never included in X.
    y = df["target"].astype(int)
    X = df.drop(columns=["target"])

    # Remove identifiers: they identify records but should not become
    # predictive signals.
    id_columns = [
        c for c in ["loan_id", "customer_id"]
        if c in X.columns
    ]
    X = X.drop(columns=id_columns)

    # Remove extremely high-cardinality free-form categorical columns if any.
    # This keeps the first portfolio model stable and reproducible.
    high_cardinality = [
        c for c in X.select_dtypes(include=["object"]).columns
        if X[c].nunique(dropna=True) > 100
    ]
    X = X.drop(columns=high_cardinality)

    categorical = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    numerical = X.select_dtypes(include=[np.number]).columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        stratify=y,
        random_state=RANDOM_STATE
    )

    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(
            handle_unknown="ignore",
            min_frequency=20
        ))
    ])

    preprocess = ColumnTransformer([
        ("numeric", numeric_pipe, numerical),
        ("categorical", categorical_pipe, categorical)
    ])

    logistic = Pipeline([
        ("preprocess", preprocess),
        ("model", LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            solver="liblinear",
            random_state=RANDOM_STATE
        ))
    ])

    logistic.fit(X_train, y_train)

    metrics_log, prob_log, pred_log = evaluate_model(
        "Logistic Regression",
        logistic,
        X_test,
        y_test
    )

    joblib.dump(
        logistic,
        MODELS / "logistic_regression.joblib"
    )

    # LightGBM needs numeric inputs, so reuse the same preprocessing.
    X_train_lgb = preprocess.fit_transform(X_train)
    X_test_lgb = preprocess.transform(X_test)

    lgbm = LGBMClassifier(
        n_estimators=400,
        learning_rate=0.05,
        num_leaves=31,
        subsample=0.80,
        colsample_bytree=0.80,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1
    )

    lgbm.fit(X_train_lgb, y_train)

    metrics_lgb, prob_lgb, pred_lgb = evaluate_model(
        "LightGBM",
        lgbm,
        X_test_lgb,
        y_test
    )

    # Save both preprocessing and model together.
    joblib.dump(
        {
            "preprocess": preprocess,
            "model": lgbm,
            "feature_columns": list(X.columns),
        },
        MODELS / "lightgbm_bundle.joblib"
    )

    metrics = pd.DataFrame([metrics_log, metrics_lgb])
    metrics.to_csv(REPORTS / "model_metrics.csv", index=False)

    predictions = pd.DataFrame({
        "actual_target": y_test.reset_index(drop=True),
        "logistic_probability": prob_log,
        "logistic_prediction": pred_log,
        "lightgbm_probability": prob_lgb,
        "lightgbm_prediction": pred_lgb,
    })

    predictions.to_csv(
        REPORTS / "model_predictions.csv",
        index=False
    )

    deciles = make_deciles(y_test.reset_index(drop=True), prob_lgb)
    deciles.to_csv(REPORTS / "score_deciles.csv", index=False)

    confusion = {
        "logistic_regression": confusion_matrix(
            y_test, pred_log
        ).tolist(),
        "lightgbm": confusion_matrix(
            y_test, pred_lgb
        ).tolist(),
    }

    (REPORTS / "confusion_matrices.json").write_text(
        json.dumps(confusion, indent=2),
        encoding="utf-8"
    )

    print("\n=== MODEL COMPARISON ===")
    print(metrics.to_string(index=False))

    print("\n=== LIGHTGBM SCORE DECILES ===")
    print(deciles.to_string(index=False))

    print("\nModel files saved under:", MODELS)


if __name__ == "__main__":
    main()
