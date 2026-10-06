
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_recall_curve


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "loan_features.csv"
MODEL_PATH = ROOT / "models" / "lightgbm_bundle.joblib"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)


def load_model():
    bundle = joblib.load(MODEL_PATH)
    if isinstance(bundle, dict):
        model = bundle["model"]
        preprocess = bundle["preprocess"]
        feature_columns = bundle.get("feature_columns")
        high_cardinality = bundle.get("dropped_high_cardinality", [])
    else:
        raise ValueError("Unexpected model bundle format.")
    return model, preprocess, feature_columns, high_cardinality


def prepare_data(df, feature_columns, high_cardinality):
    target = "target"
    drop_cols = [target, "loan_id", "customer_id"]

    X = df.drop(columns=[c for c in drop_cols if c in df.columns]).copy()
    y = df[target].astype(int).copy()

    if feature_columns:
        keep = [c for c in feature_columns if c in X.columns]
        X = X[keep]

    drop_hc = [c for c in high_cardinality if c in X.columns]
    if drop_hc:
        X = X.drop(columns=drop_hc)

    return X, y


def main():
    if not DATA.exists():
        raise FileNotFoundError(f"Missing {DATA}. Run 03_feature_engineering.py first.")
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Missing {MODEL_PATH}. Run 04_modeling.py first.")

    df = pd.read_csv(DATA)
    model, preprocess, feature_columns, high_cardinality = load_model()

    X, y = prepare_data(df, feature_columns, high_cardinality)

    # Recreate the same stratified split used by the modeling script.
    idx = np.arange(len(df))
    train_idx, test_idx = train_test_split(
        idx, test_size=0.20, random_state=42, stratify=y
    )

    X_test = X.iloc[test_idx].copy()
    y_test = y.iloc[test_idx].copy()

    X_test_t = preprocess.transform(X_test)

    # ---- SHAP explainability ----
    sample_n = min(3000, X_test_t.shape[0])
    rng = np.random.default_rng(42)
    sample_idx = rng.choice(X_test_t.shape[0], size=sample_n, replace=False)
    X_shap = X_test_t[sample_idx]

    feature_names = list(preprocess.get_feature_names_out())

    # SHAP TreeExplainer is appropriate for the LightGBM tree model.
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_shap)

    if isinstance(shap_values, list):
        shap_matrix = shap_values[1]
    else:
        shap_matrix = shap_values

    mean_abs = np.abs(shap_matrix).mean(axis=0)
    shap_importance = (
        pd.DataFrame({
            "feature": feature_names,
            "mean_abs_shap": mean_abs
        })
        .sort_values("mean_abs_shap", ascending=False)
    )
    shap_importance.to_csv(REPORTS / "shap_feature_importance.csv", index=False)

    # Summary bar plot (stable and portfolio-friendly).
    top = shap_importance.head(20).sort_values("mean_abs_shap")
    plt.figure(figsize=(10, 7))
    plt.barh(top["feature"], top["mean_abs_shap"])
    plt.xlabel("Mean absolute SHAP value")
    plt.ylabel("Feature")
    plt.title("Top Drivers of Model Prediction")
    plt.tight_layout()
    plt.savefig(FIGURES / "05_shap_feature_importance.png", dpi=160)
    plt.close()

    # ---- Business scoring ----
    test_df = df.iloc[test_idx].copy()
    X_test_full = X.iloc[test_idx]
    pd_test = model.predict_proba(preprocess.transform(X_test_full))[:, 1]

    scoring = test_df[[
        c for c in ["loan_id", "customer_id", "target", "credit_amount", "income"]
        if c in test_df.columns
    ]].copy()

    scoring["predicted_pd"] = pd_test
    scoring["risk_band"] = pd.cut(
        scoring["predicted_pd"],
        bins=[-np.inf, 0.05, 0.10, 0.20, np.inf],
        labels=["Low", "Medium", "High", "Very High"],
        right=False
    )

    # Illustrative portfolio assumption; clearly label this in README/report.
    LGD = 0.45
    if "credit_amount" in scoring.columns:
        scoring["ead"] = pd.to_numeric(scoring["credit_amount"], errors="coerce").fillna(0)
    else:
        scoring["ead"] = 0.0

    scoring["expected_loss"] = scoring["predicted_pd"] * LGD * scoring["ead"]

    scoring.sort_values(
        ["expected_loss", "predicted_pd"], ascending=False
    ).to_csv(REPORTS / "risk_action_list.csv", index=False)

    # ---- Threshold analysis ----
    thresholds = np.arange(0.05, 0.31, 0.025)
    rows = []
    for threshold in thresholds:
        flagged = pd_test >= threshold
        total_flagged = int(flagged.sum())
        defaults_captured = int(y_test[flagged].sum())
        total_defaults = int(y_test.sum())

        rows.append({
            "threshold": round(float(threshold), 3),
            "flagged_loans": total_flagged,
            "flagged_rate": round(total_flagged / len(y_test), 4),
            "defaults_captured": defaults_captured,
            "default_capture_rate": round(
                defaults_captured / total_defaults, 4
            ) if total_defaults else np.nan,
            "precision": round(
                defaults_captured / total_flagged, 4
            ) if total_flagged else np.nan
        })

    threshold_df = pd.DataFrame(rows)
    threshold_df.to_csv(REPORTS / "risk_threshold_analysis.csv", index=False)

    # ---- Score deciles ----
    deciles = scoring.copy()
    deciles["score_decile"] = pd.qcut(
        deciles["predicted_pd"].rank(method="first"),
        10,
        labels=False
    ) + 1

    decile_summary = (
        deciles.groupby("score_decile", as_index=False)
        .agg(
            loans=("predicted_pd", "size"),
            avg_pd=("predicted_pd", "mean"),
            actual_default_rate=("target", "mean"),
            avg_expected_loss=("expected_loss", "mean")
        )
        .sort_values("score_decile")
    )
    decile_summary.to_csv(REPORTS / "score_decile_business_summary.csv", index=False)

    print("Step 7 completed.")
    print(f"SHAP sample: {sample_n:,} rows")
    print("\nTop 10 SHAP drivers:")
    print(shap_importance.head(10).to_string(index=False))
    print("\nRisk bands:")
    print(scoring["risk_band"].value_counts(dropna=False).to_string())
    print("\nFiles written to reports/ and reports/figures/.")


if __name__ == "__main__":
    main()
