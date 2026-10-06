"""
01_profile_dataset.py
Loan Default Risk Analytics

Purpose:
- Inspect the Home Credit CSV files placed under data/raw/
- Report row count, column count, data types, missingness and unique counts
- Create a machine-readable profile under reports/data_profile/
- Do NOT modify the raw files

Run from project root:
    python python/01_profile_dataset.py
"""

from pathlib import Path
import pandas as pd
import json

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "reports" / "data_profile"
OUT.mkdir(parents=True, exist_ok=True)

if not RAW.exists():
    raise FileNotFoundError(f"Raw data folder not found: {RAW}")

csv_files = sorted(RAW.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(
        f"No CSV files found in {RAW}. Download the dataset and place the CSV files there."
    )

summary = []

for file in csv_files:
    print(f"\nProfiling: {file.name}")

    # Read only the header first to determine columns.
    header = pd.read_csv(file, nrows=0)
    columns = header.columns.tolist()

    # Read data in chunks so profiling does not require loading the entire
    # large dataset into memory at once.
    row_count = 0
    null_counts = pd.Series(0, index=columns, dtype="int64")
    unique_counts = pd.Series(0, index=columns, dtype="int64")
    dtypes = {}

    for chunk in pd.read_csv(file, chunksize=50_000, low_memory=False):
        row_count += len(chunk)

        null_counts = null_counts.add(chunk.isna().sum(), fill_value=0)

        for col in columns:
            unique_counts[col] += chunk[col].nunique(dropna=True)

        for col in columns:
            dtypes[col] = str(chunk[col].dtype)

    profile = pd.DataFrame({
        "column": columns,
        "dtype": [dtypes.get(c, "unknown") for c in columns],
        "null_count": [int(null_counts[c]) for c in columns],
        "null_pct": [
            round((null_counts[c] / row_count) * 100, 4) if row_count else None
            for c in columns
        ],
        "observed_unique_count": [int(unique_counts[c]) for c in columns],
    })

    profile_file = OUT / f"{file.stem}_profile.csv"
    profile.to_csv(profile_file, index=False)

    summary.append({
        "file": file.name,
        "rows": int(row_count),
        "columns": len(columns),
        "profile_file": str(profile_file.relative_to(ROOT)),
    })

    print(f"Rows: {row_count:,}")
    print(f"Columns: {len(columns):,}")
    print(f"Profile saved: {profile_file}")

summary_file = OUT / "dataset_summary.json"
summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")

print("\n=== DATASET SUMMARY ===")
for item in summary:
    print(f"{item['file']}: {item['rows']:,} rows x {item['columns']:,} columns")

print(f"\nSummary saved to: {summary_file}")
