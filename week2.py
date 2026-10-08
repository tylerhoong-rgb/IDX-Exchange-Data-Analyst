"""

this script:

  1. Documents dataset structure (rows/cols, dtypes) and splits columns
     into market analysis fields vs. metadata fields.
     
  2. Produces a missing-value report, flags any column >90% null
    Decides which columns to drop vs. retain (keep core fields even if partially missing)

  3. Produces a numeric
    distribution summary (min, max, mean, median, percentiles) for ClosePrice, LivingArea, and
    DaysOnMarket.

  4. Answers the Suggested Intern Questions using the data.


Outputs (written to OUTPUT_DIR):
    CRMLSListing_Residential_Filtered.csv
    CRMLSSold_Residential_Filtered.csv
    <label>_missing_value_report.csv
    <label>_numeric_distribution_summary.csv
    plots/<label>_<field>_hist.png
    plots/<label>_<field>_box.png
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # no display needed, just save PNGs
import matplotlib.pyplot as plt

# CONFIG
INPUT_DIR = "Week1 Output"
OUTPUT_DIR = "Week2 Output"
PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")

LISTING_INPUT_FILE = os.path.join(INPUT_DIR, "CRMLSListing_Residential_Combined.csv")
SOLD_INPUT_FILE = os.path.join(INPUT_DIR, "CRMLSSold_Residential_Combined.csv")

# Fields analyzed in the "Numeric Distribution Review" section
NUMERIC_REVIEW_FIELDS = [
    "ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea",
    "LotSizeAcres", "BedroomsTotal", "BathroomsTotalInteger",
    "DaysOnMarket", "YearBuilt",
]

# The three fields the deliverable explicitly requires a summary table for
REQUIRED_SUMMARY_FIELDS = ["ClosePrice", "LivingArea", "DaysOnMarket"]

# Core fields we keep even if partially missing (never auto-dropped)
CORE_FIELDS = [
    "ListingId", "ListingKey", "PropertyType", "MlsStatus",
    "ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea",
    "LotSizeAcres", "BedroomsTotal", "BathroomsTotalInteger",
    "DaysOnMarket", "YearBuilt", "City", "CountyOrParish", "PostalCode",
    "ListingContractDate", "CloseDate", "ContractStatusChangeDate",
]

# Keyword-based split: "market analysis" fields vs. "metadata" fields
MARKET_KEYWORDS = [
    "price", "list", "close", "area", "sqft", "lot", "acre", "bed",
    "bath", "room", "yearbuilt", "dom", "dayson", "county", "city",
    "zip", "postal", "propertytype", "status", "contractdate",
]
METADATA_KEYWORDS = [
    "id", "key", "agent", "office", "broker", "mls", "source",
    "modificationtimestamp", "createdby", "url", "photo", "remark",
    "compliance", "internet", "originatingsystem", "aor",
]


# file loading helpers
def dedupe_columns(df: pd.DataFrame, label: str) -> pd.DataFrame:
    """The raw CRMLS export files contain duplicate column headers (e.g.
    PropertyType and PropertyType.1). pandas auto-suffixes these with
    '.1' on read. This helper drops the '.1' duplicate whenever it is
    byte-for-byte identical to the original column, and warns about any
    that differ (which would need manual review)."""
    dupe_cols = [c for c in df.columns if c.endswith(".1")]
    for dupe in dupe_cols:
        base = dupe[:-2]
        if base in df.columns:
            if df[base].equals(df[dupe]):
                df = df.drop(columns=[dupe])
            else:
                mismatch = (df[base] != df[dupe]).sum()
                print(f"  [WARNING] {label}: '{base}' and '{dupe}' differ in "
                      f"{mismatch} rows; keeping both for manual review.")
    if dupe_cols:
        print(f"  {label}: found {len(dupe_cols)} duplicate-header columns in "
              f"source file, resolved by de-duplication above.")
    return df


def load_combined(file_path: str, label: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{label}: expected combined file not found -> {file_path}")
    df = pd.read_csv(file_path, low_memory=False)
    print(f"  {label}: loaded {file_path} -> {len(df)} rows, {len(df.columns)} columns")
    df = dedupe_columns(df, label)
    return df


# Dataset understanding
def dataset_understanding(df: pd.DataFrame, label: str):
    print(f"\n--- [{label}] Dataset Understanding ---")
    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    print("Column dtypes:")
    print(df.dtypes)

    cols_lower = {c: c.lower() for c in df.columns}
    market_fields = [c for c, cl in cols_lower.items()
                      if any(k in cl for k in MARKET_KEYWORDS)
                      and not any(k in cl for k in METADATA_KEYWORDS)]
    metadata_fields = [c for c in df.columns if c not in market_fields]

    print(f"Market analysis fields ({len(market_fields)}): {market_fields}")
    print(f"Metadata fields ({len(metadata_fields)}): {metadata_fields}")
    return market_fields, metadata_fields


# Missing value analysis
def missing_value_report(df: pd.DataFrame, label: str) -> pd.DataFrame:
    print(f"\n--- [{label}] Missing Value Analysis ---")
    null_counts = df.isnull().sum()
    null_pct = (null_counts / len(df) * 100).round(2)
    report = pd.DataFrame({
        "column": df.columns,
        "null_count": null_counts.values,
        "null_pct": null_pct.values,
    }).sort_values("null_pct", ascending=False).reset_index(drop=True)

    high_missing = report[report["null_pct"] > 90]
    print(f"Columns >90% missing ({len(high_missing)}):")
    print(high_missing[["column", "null_pct"]].to_string(index=False) if len(high_missing) else "  None")

    # Decision: drop >90% missing UNLESS the column is a core field
    report["decision"] = np.where(
        (report["null_pct"] > 90) & (~report["column"].isin(CORE_FIELDS)),
        "DROP (>90% null, not core)",
        np.where(
            (report["null_pct"] > 90) & (report["column"].isin(CORE_FIELDS)),
            "RETAIN (core field, despite >90% null)",
            "RETAIN",
        ),
    )

    report_path = os.path.join(OUTPUT_DIR, f"{label}_missing_value_report.csv")
    report.to_csv(report_path, index=False)
    print(f"Saved missing value report -> {report_path}")
    return report


def apply_drop_decisions(df: pd.DataFrame, report: pd.DataFrame) -> pd.DataFrame:
    drop_cols = report.loc[report["decision"].str.startswith("DROP"), "column"].tolist()
    if drop_cols:
        print(f"Dropping {len(drop_cols)} columns: {drop_cols}")
    return df.drop(columns=drop_cols, errors="ignore")


# Property type documentation + Residential filter
def document_and_filter_residential(df: pd.DataFrame, label: str) -> pd.DataFrame:
    print(f"\n--- [{label}] Property Type Filtering ---")
    if "PropertyType" not in df.columns:
        print("  [WARNING] No PropertyType column found; skipping filter.")
        return df

    type_counts = df["PropertyType"].value_counts(dropna=False)
    print("Unique PropertyType values found (with counts):")
    print(type_counts.to_string())

    rows_before = len(df)
    # Filtering logic: keep only rows where PropertyType == 'Residential'
    filtered = df[df["PropertyType"] == "Residential"].copy()
    rows_after = len(filtered)

    print(f"Rows BEFORE Residential filter: {rows_before}")
    print(f"Rows AFTER Residential filter:  {rows_after}")
    residential_share = round(rows_after / rows_before * 100, 2) if rows_before else 0
    print(f"Residential share of dataset: {residential_share}%")

    return filtered


# numeric distribution review
def numeric_distribution_review(df: pd.DataFrame, label: str):
    print(f"\n--- [{label}] Numeric Distribution Review ---")
    os.makedirs(PLOTS_DIR, exist_ok=True)

    summary_rows = []
    fields_present = [f for f in NUMERIC_REVIEW_FIELDS if f in df.columns]
    missing_fields = [f for f in NUMERIC_REVIEW_FIELDS if f not in df.columns]
    if missing_fields:
        print(f"  [WARNING] Fields not found in {label}, skipped: {missing_fields}")

    for field in fields_present:
        series = pd.to_numeric(df[field], errors="coerce").dropna()
        if series.empty:
            continue

        stats = {
            "field": field,
            "count": series.count(),
            "min": series.min(),
            "p1": series.quantile(0.01),
            "p25": series.quantile(0.25),
            "median": series.median(),
            "mean": series.mean(),
            "p75": series.quantile(0.75),
            "p95": series.quantile(0.95),
            "p99": series.quantile(0.99),
            "max": series.max(),
            "std": series.std(),
        }
        summary_rows.append(stats)

        # Extreme outlier flag using 1.5*IQR rule
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n_outliers = ((series < lower) | (series > upper)).sum()
        print(f"  {field}: {n_outliers} extreme outliers flagged (1.5xIQR rule, "
              f"bounds ~[{lower:.2f}, {upper:.2f}])")

        # Histogram
        plt.figure(figsize=(6, 4))
        series.plot(kind="hist", bins=40, edgecolor="black")
        plt.title(f"{label}: {field} Histogram")
        plt.xlabel(field)
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, f"{label}_{field}_hist.png"))
        plt.close()

        # Boxplot
        plt.figure(figsize=(4, 5))
        plt.boxplot(series, vert=True)
        plt.title(f"{label}: {field} Boxplot")
        plt.ylabel(field)
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, f"{label}_{field}_box.png"))
        plt.close()

    full_summary = pd.DataFrame(summary_rows)
    summary_path = os.path.join(OUTPUT_DIR, f"{label}_numeric_distribution_summary.csv")
    full_summary.to_csv(summary_path, index=False)
    print(f"Saved full numeric distribution summary -> {summary_path}")

    # Required focused table: ClosePrice, LivingArea, DaysOnMarket
    required_present = [f for f in REQUIRED_SUMMARY_FIELDS if f in full_summary["field"].values]
    if required_present:
        focused = full_summary[full_summary["field"].isin(required_present)]
        print("\nRequired numeric summary (ClosePrice, LivingArea, DaysOnMarket):")
        print(focused.to_string(index=False))
    else:
        print("  [WARNING] None of ClosePrice/LivingArea/DaysOnMarket present in this dataset.")

    return full_summary


# Intern Questions
def answer_intern_questions(raw_df: pd.DataFrame, residential_df: pd.DataFrame, label: str):
    print(f"\n--- [{label}] Suggested Intern Questions ---")

    # Q1: Residential vs other property type share
    if "PropertyType" in raw_df.columns:
        share = (raw_df["PropertyType"].value_counts(normalize=True) * 100).round(2)
        print("Q1: Residential vs. other PropertyType share (%):")
        print(share.to_string())

    # Q2: Median and average close price
    if "ClosePrice" in residential_df.columns:
        cp = pd.to_numeric(residential_df["ClosePrice"], errors="coerce").dropna()
        print(f"Q2: Median ClosePrice: {cp.median():,.2f} | Average ClosePrice: {cp.mean():,.2f}")

    # Q3: Days on Market distribution
    if "DaysOnMarket" in residential_df.columns:
        dom = pd.to_numeric(residential_df["DaysOnMarket"], errors="coerce").dropna()
        print("Q3: DaysOnMarket distribution (min/25/50/75/max):")
        print(dom.describe(percentiles=[0.25, 0.5, 0.75]).to_string())

    # Q4: % sold above vs. below list price 
    if {"ClosePrice", "ListPrice"}.issubset(residential_df.columns):
        tmp = residential_df[["ClosePrice", "ListPrice"]].apply(pd.to_numeric, errors="coerce").dropna()
        above = (tmp["ClosePrice"] > tmp["ListPrice"]).mean() * 100
        below = (tmp["ClosePrice"] < tmp["ListPrice"]).mean() * 100
        at = (tmp["ClosePrice"] == tmp["ListPrice"]).mean() * 100
        print(f"Q4: Sold above list: {above:.2f}% | below list: {below:.2f}% | at list: {at:.2f}%")

    # Q5: Date consistency (CloseDate before ListingContractDate)
    date_cols_present = {"CloseDate", "ListingContractDate"}.issubset(residential_df.columns)
    if date_cols_present:
        cd = pd.to_datetime(residential_df["CloseDate"], errors="coerce")
        ld = pd.to_datetime(residential_df["ListingContractDate"], errors="coerce")
        both_present = cd.notna() & ld.notna()
        bad_dates = (cd < ld)[both_present].sum()
        print(f"Q5: Rows where CloseDate is before ListingContractDate (data issue): "
              f"{bad_dates} (out of {both_present.sum()} rows with both dates populated)")

    # Q6: Counties with highest median price
    price_col = "ClosePrice" if "ClosePrice" in residential_df.columns else "ListPrice"
    if "CountyOrParish" in residential_df.columns and price_col in residential_df.columns:
        tmp = residential_df[["CountyOrParish", price_col]].copy()
        tmp[price_col] = pd.to_numeric(tmp[price_col], errors="coerce")
        top_counties = tmp.groupby("CountyOrParish")[price_col].median().sort_values(ascending=False).head(10)
        print(f"Q6: Top 10 counties by median {price_col}:")
        print(top_counties.to_string())


# PIPELINE
def run_pipeline(input_file: str, label: str, output_filename: str):
    print(f"\n============================ {label.upper()} ============================")
    raw_df = load_combined(input_file, label)

    dataset_understanding(raw_df, label)
    missing_report = missing_value_report(raw_df, label)
    trimmed_df = apply_drop_decisions(raw_df, missing_report)

    residential_df = document_and_filter_residential(trimmed_df, label)

    print(f"\n--- [{label}] Null-count summary table (post-filter) ---")
    post_filter_nulls = residential_df.isnull().sum().sort_values(ascending=False)
    print(post_filter_nulls.to_string())

    numeric_distribution_review(residential_df, label)
    answer_intern_questions(raw_df, residential_df, label)

    out_path = os.path.join(OUTPUT_DIR, output_filename)
    residential_df.to_csv(out_path, index=False)
    print(f"\nSaved Residential-filtered dataset -> {out_path}")
    return residential_df


def main():
    run_pipeline(LISTING_INPUT_FILE, "Listing", "CRMLSListing_Residential_Filtered.csv")
    run_pipeline(SOLD_INPUT_FILE, "Sold", "CRMLSSold_Residential_Filtered.csv")

    print("\nDone.")


if __name__ == "__main__":
    main()
