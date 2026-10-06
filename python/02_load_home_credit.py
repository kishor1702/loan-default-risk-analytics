"""
02_load_home_credit.py

Creates PostgreSQL staging tables automatically from the CSV headers and
loads the CSV files using PostgreSQL COPY.

Before running:
1. Create database: loan_default_risk
2. Install requirements.txt
3. Set environment variables:
   PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD

Example (PowerShell):
$env:PGHOST="localhost"
$env:PGPORT="5432"
$env:PGDATABASE="loan_default_risk"
$env:PGUSER="postgres"
$env:PGPASSWORD="your_password"

Run:
python python/02_load_home_credit.py
"""

from pathlib import Path
import csv
import os
import re

import psycopg2
from psycopg2 import sql

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

FILES = {
    "application_train": RAW / "application_train.csv",
    "bureau": RAW / "bureau.csv",
    "previous_application": RAW / "previous_application.csv",
}

def clean_identifier(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if not name:
        name = "column"
    if name[0].isdigit():
        name = "_" + name
    return name

def get_headers(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        return next(reader)

def connect():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "loan_default_risk"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD"),
    )

def create_staging_table(cur, table_name, headers):
    # Use TEXT for raw staging. Type conversion happens later.
    columns = []
    seen = set()

    for original in headers:
        col = clean_identifier(original)
        if col in seen:
            raise ValueError(f"Duplicate normalized column name: {col}")
        seen.add(col)
        columns.append(sql.SQL("{} TEXT").format(sql.Identifier(col)))

    query = sql.SQL(
        "DROP TABLE IF EXISTS credit_risk_staging.{}; "
        "CREATE TABLE credit_risk_staging.{} ({})"
    ).format(
        sql.Identifier(table_name),
        sql.Identifier(table_name),
        sql.SQL(", ").join(columns),
    )
    cur.execute(query)

def copy_csv(cur, table_name, path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        copy_sql = sql.SQL(
            "COPY credit_risk_staging.{} FROM STDIN "
            "WITH (FORMAT CSV, HEADER TRUE, NULL '', QUOTE '\"', ESCAPE '\"')"
        ).format(sql.Identifier(table_name))
        cur.copy_expert(copy_sql.as_string(cur), f)

def main():
    missing = [str(p) for p in FILES.values() if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing CSV files:\n" + "\n".join(missing)
        )

    conn = connect()
    try:
        conn.autocommit = False
        cur = conn.cursor()

        cur.execute("CREATE SCHEMA IF NOT EXISTS credit_risk_staging;")
        cur.execute("CREATE SCHEMA IF NOT EXISTS credit_risk;")

        for table_name, path in FILES.items():
            print(f"\nLoading {path.name} ...")
            headers = get_headers(path)
            print(f"Detected {len(headers)} columns.")

            create_staging_table(cur, table_name, headers)
            copy_csv(cur, table_name, path)

            cur.execute(
                sql.SQL("SELECT COUNT(*) FROM credit_risk_staging.{}")
                .format(sql.Identifier(table_name))
            )
            rows = cur.fetchone()[0]
            print(f"Loaded {rows:,} rows into credit_risk_staging.{table_name}")

        conn.commit()
        print("\nSUCCESS: all staging tables loaded.")

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
