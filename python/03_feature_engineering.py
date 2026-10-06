"""
03_feature_engineering.py
Leakage-aware feature engineering for Loan Default Risk Analytics.

Important:
Features must represent information available at or before the
loan decision point. Do not use target-derived or post-decision
repayment variables.
"""

from pathlib import Path
import os

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]

def get_engine():
    password = os.getenv("PGPASSWORD")
    if not password:
        raise RuntimeError("Set PGPASSWORD before running this script.")

    return create_engine(
        f"postgresql+psycopg2://"
        f"{os.getenv('PGUSER', 'postgres')}:{password}@"
        f"{os.getenv('PGHOST', 'localhost')}:"
        f"{os.getenv('PGPORT', '5432')}/"
        f"{os.getenv('PGDATABASE', 'loan_default_risk')}"
    )

def add_features(df):
    out = df.copy()

    # Financial capacity
    out["credit_income_ratio"] = (
        out["credit_amount"] /
        out["income_amount"].replace(0, np.nan)
    )

    out["annuity_income_ratio"] = (
        out["annuity_amount"] /
        out["income_amount"].replace(0, np.nan)
    )

    # Approximate age from negative days_birth
    out["age_years"] = (
        out["days_birth"].abs() / 365.25
    )

    # Employment duration
    out["employment_years"] = (
        out["days_employed"].clip(upper=0).abs() / 365.25
    )

    # Credit amount relative to goods price
    out["credit_goods_ratio"] = (
        out["credit_amount"] /
        out["goods_price"].replace(0, np.nan)
    )

    # External score average
    score_cols = [
        c for c in [
            "ext_source_1",
            "ext_source_2",
            "ext_source_3"
        ] if c in out.columns
    ]

    if score_cols:
        out["external_score_mean"] = out[score_cols].mean(axis=1)
        out["external_score_missing_count"] = (
            out[score_cols].isna().sum(axis=1)
        )

    # Log transforms for highly skewed monetary variables
    for col in ["income_amount", "credit_amount", "annuity_amount", "goods_price"]:
        if col in out.columns:
            out[f"log_{col}"] = np.log1p(out[col].clip(lower=0))

    # Risk bands
    out["credit_income_band"] = pd.cut(
        out["credit_income_ratio"],
        bins=[-np.inf, 1, 2, 4, np.inf],
        labels=["<1x", "1x-2x", "2x-4x", "4x+"]
    )

    out["age_band"] = pd.cut(
        out["age_years"],
        bins=[0, 25, 35, 45, 55, np.inf],
        labels=["<25", "25-34", "35-44", "45-54", "55+"]
    )

    return out

def main():
    engine = get_engine()

    query = """
        SELECT *
        FROM credit_risk.loan_application;
    """

    df = pd.read_sql(text(query), engine)
    print(f"Loaded {len(df):,} rows.")

    # Explicitly keep target separate from features.
    target = df["target"].copy()
    features = df.drop(columns=["target"])

    # Feature engineering occurs without using target.
    features = add_features(features)
    features["target"] = target

    output = ROOT / "data" / "processed" / "loan_features.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output, index=False)

    print(f"Saved: {output}")
    print(f"Feature count: {features.shape[1] - 1}")

if __name__ == "__main__":
    main()
