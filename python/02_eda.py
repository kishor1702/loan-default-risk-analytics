"""
02_eda.py
Loan Default Risk Analytics — Python EDA

Reads the typed PostgreSQL loan_application table and produces:
- dataset shape
- target distribution
- missingness
- numeric summary
- categorical summaries
- basic risk-driver plots

Run from project root after PostgreSQL is populated.
"""

from pathlib import Path
import os

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "reports" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

def get_engine():
    password = os.getenv("PGPASSWORD")
    if not password:
        raise RuntimeError("Set PGPASSWORD before running this script.")

    url = (
        f"postgresql+psycopg2://"
        f"{os.getenv('PGUSER', 'postgres')}:{password}@"
        f"{os.getenv('PGHOST', 'localhost')}:"
        f"{os.getenv('PGPORT', '5432')}/"
        f"{os.getenv('PGDATABASE', 'loan_default_risk')}"
    )
    return create_engine(url)

def main():
    engine = get_engine()

    query = """
        SELECT
            loan_id,
            customer_id,
            contract_type,
            gender,
            owns_car,
            owns_realty,
            income_type,
            education_type,
            family_status,
            occupation_type,
            organization_type,
            income_amount,
            credit_amount,
            annuity_amount,
            goods_price,
            days_birth,
            days_employed,
            region_population_relative,
            ext_source_1,
            ext_source_2,
            ext_source_3,
            target
        FROM credit_risk.loan_application;
    """

    df = pd.read_sql(text(query), engine)

    print("\n=== DATASET ===")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {df.shape[1]:,}")

    print("\n=== TARGET ===")
    print(df["target"].value_counts(dropna=False))
    print("\nTarget rate:")
    print(df["target"].mean())

    print("\n=== MISSINGNESS ===")
    missing = (
        df.isna()
          .mean()
          .mul(100)
          .sort_values(ascending=False)
          .rename("missing_pct")
    )
    print(missing.head(20))

    missing.head(20).to_csv(
        ROOT / "reports" / "top_missing_columns.csv"
    )

    print("\n=== NUMERIC SUMMARY ===")
    numeric_cols = df.select_dtypes(include="number").columns
    summary = df[numeric_cols].describe().T
    summary.to_csv(ROOT / "reports" / "numeric_summary.csv")
    print(summary)

    # Target distribution
    plt.figure(figsize=(7, 5))
    sns.countplot(data=df, x="target")
    plt.title("Loan Default Target Distribution")
    plt.xlabel("Default Target")
    plt.ylabel("Applications")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "01_target_distribution.png", dpi=150)
    plt.close()

    # Credit amount by target
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df, x="target", y="credit_amount")
    plt.ylim(0, df["credit_amount"].quantile(0.99))
    plt.title("Credit Amount by Default Outcome")
    plt.xlabel("Default Target")
    plt.ylabel("Credit Amount")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "02_credit_by_target.png", dpi=150)
    plt.close()

    # External score
    if "ext_source_2" in df.columns:
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=df, x="target", y="ext_source_2")
        plt.title("External Score 2 by Default Outcome")
        plt.xlabel("Default Target")
        plt.ylabel("External Score 2")
        plt.tight_layout()
        plt.savefig(FIG_DIR / "03_ext_source_2_by_target.png", dpi=150)
        plt.close()

    # Income type
    if "income_type" in df.columns:
        top_types = (
            df["income_type"]
            .value_counts()
            .head(10)
            .index
        )
        plot_df = df[df["income_type"].isin(top_types)]
        rates = (
            plot_df.groupby("income_type")["target"]
            .mean()
            .sort_values(ascending=False)
        )

        plt.figure(figsize=(10, 6))
        rates.mul(100).plot(kind="bar")
        plt.title("Default Rate by Income Type")
        plt.ylabel("Default Rate (%)")
        plt.xlabel("Income Type")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(FIG_DIR / "04_default_rate_income_type.png", dpi=150)
        plt.close()

    print("\nEDA complete.")
    print(f"Figures saved under: {FIG_DIR}")

if __name__ == "__main__":
    main()
