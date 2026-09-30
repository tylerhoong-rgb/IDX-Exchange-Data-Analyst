"""
Week 7 Deliverable: Outlier Detection and Data Quality


  Tier 1 -- Business rules (already applied upstream, Weeks 4-5):
            ClosePrice <= 0, LivingArea <= 0, DaysOnMarket < 0, etc.
            A record failing these is invalid outright, full stop --
            IQR is not what determines that.

  Tier 2 -- Statistical outliers (this script, IQR method):
            For each of ClosePrice, LivingArea, DaysOnMarket (the three
            fields the deliverable names), plus price_per_sqft and
            close_to_original_list_ratio (the two additional fields the
            handbook's intro paragraph calls out as distortion-prone),
            Q1/Q3/IQR are computed using ONLY rows that are already
            Tier-1-valid for that field. This matters: including the
            business-rule-invalid rows (e.g. ClosePrice == 0) in the
            IQR calculation would drag Q1 down and distort the bounds
            for everyone else. Rows outside [Q1-1.5*IQR, Q1+1.5*IQR]
            are FLAGGED, never silently dropped.

  Combined  -- any_outlier_flag = Tier 1 OR Tier 2, for any of the
               five fields above.

Two outputs are saved, per the "flag vs. remove" principle:
  - A FULL flagged dataset: every input row, with all flag columns
    added, nothing removed. This is the audit trail.
  - A FILTERED analysis dataset: input rows with any_outlier_flag ==
    False, i.e. Tier-1-valid AND not a Tier-2 statistical outlier on
    any of the five fields. This is what Tableau / summary analysis
    should read from.

A written before/after comparison (row counts + median ClosePrice,
LivingArea, DaysOnMarket) is printed for both datasets.

Input:
    CRMLSSold_Residential_WithMetrics.csv
    CRMLSListing_Residential_WithMetrics.csv

Output:
    CRMLSSold_Residential_Flagged.csv
    CRMLSSold_Residential_FilteredForAnalysis.csv
    CRMLSListing_Residential_Flagged.csv
    CRMLSListing_Residential_FilteredForAnalysis.csv
"""

import os
import pandas as pd

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
INPUT_DIR = "Week6 Output"
OUTPUT_DIR = "Week7 Output"

SOLD_INPUT_FILE = os.path.join(INPUT_DIR, "CRMLSSold_Residential_WithMetrics.csv")
LISTING_INPUT_FILE = os.path.join(INPUT_DIR, "CRMLSListing_Residential_WithMetrics.csv")

SOLD_FLAGGED_FILE = os.path.join(OUTPUT_DIR, "CRMLSSold_Residential_Flagged.csv")
SOLD_FILTERED_FILE = os.path.join(OUTPUT_DIR, "CRMLSSold_Residential_FilteredForAnalysis.csv")
LISTING_FLAGGED_FILE = os.path.join(OUTPUT_DIR, "CRMLSListing_Residential_Flagged.csv")
LISTING_FILTERED_FILE = os.path.join(OUTPUT_DIR, "CRMLSListing_Residential_FilteredForAnalysis.csv")

# field -> the Tier-1 business-rule flag column (from Weeks 4-5) that
# already marks it definitively invalid, if one exists for that field.
IQR_FIELDS = {
    "ClosePrice": "invalid_close_price_flag",
    "LivingArea": "invalid_living_area_flag",
    "DaysOnMarket": "invalid_dom_flag",
    "price_per_sqft": None,                    # no Tier-1 rule; Tier 2 only
    "close_to_original_list_ratio": None,       # no Tier-1 rule; Tier 2 only
}

IQR_MULTIPLIER = 1.5

# The three fields the deliverable explicitly requires
REQUIRED_MEDIAN_COMPARISON_FIELDS = ["ClosePrice", "LivingArea", "DaysOnMarket"]


# ---------------------------------------------------------------------------
# STEP 1 - Tier 2: IQR-based statistical outlier flags
# ---------------------------------------------------------------------------
def flag_iqr_outliers(df: pd.DataFrame, field: str, tier1_flag_col: str | None,
                       label: str) -> pd.DataFrame:
    df = df.copy()
    flag_col = f"outlier_{field}_flag"

    if field not in df.columns:
        print(f"  [SKIP] {field} not present in {label}")
        df[flag_col] = False
        return df

    values = pd.to_numeric(df[field], errors="coerce")

    # Compute Q1/Q3 on Tier-1-valid, non-null values only -- do NOT let
    # business-rule-invalid rows (e.g. ClosePrice == 0) distort the bounds.
    if tier1_flag_col and tier1_flag_col in df.columns:
        eligible = values.notnull() & ~df[tier1_flag_col].astype(bool)
    else:
        eligible = values.notnull()

    q1 = values[eligible].quantile(0.25)
    q3 = values[eligible].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - IQR_MULTIPLIER * iqr
    upper = q3 + IQR_MULTIPLIER * iqr

    is_outlier = eligible & ((values < lower) | (values > upper))
    df[flag_col] = is_outlier.fillna(False)

    p1, p5, p95, p99 = (values[eligible].quantile(q) for q in (0.01, 0.05, 0.95, 0.99))
    print(f"  {field}: Q1={q1:,.2f}  Q3={q3:,.2f}  IQR={iqr:,.2f}  "
          f"bounds=[{lower:,.2f}, {upper:,.2f}]")
    print(f"    percentiles for context -- p1={p1:,.2f}  p5={p5:,.2f}  "
          f"p95={p95:,.2f}  p99={p99:,.2f}")
    print(f"    {flag_col}: {int(df[flag_col].sum())} rows flagged as "
          f"statistical outliers ({df[flag_col].mean() * 100:.2f}% of all rows)")

    return df


# ---------------------------------------------------------------------------
# STEP 2 - Combine Tier 1 + Tier 2 into a single any_outlier_flag
# ---------------------------------------------------------------------------
def combine_outlier_flags(df: pd.DataFrame, label: str) -> pd.DataFrame:
    df = df.copy()
    tier1_cols = [c for c in set(v for v in IQR_FIELDS.values() if v) if c in df.columns]
    tier2_cols = [f"outlier_{f}_flag" for f in IQR_FIELDS if f"outlier_{f}_flag" in df.columns]

    all_flag_cols = tier1_cols + tier2_cols
    df["any_outlier_flag"] = df[all_flag_cols].any(axis=1)

    print(f"\n--- [{label}] Combined Outlier Summary ---")
    print(f"  Tier 1 (business-rule invalid) columns used: {tier1_cols}")
    print(f"  Tier 2 (IQR statistical outlier) columns used: {tier2_cols}")
    print(f"  any_outlier_flag: {int(df['any_outlier_flag'].sum())} rows "
          f"({df['any_outlier_flag'].mean() * 100:.2f}%) flagged by at least one rule")
    return df


# ---------------------------------------------------------------------------
# STEP 3 - Written before/after comparison
# ---------------------------------------------------------------------------
def print_before_after_comparison(full_df: pd.DataFrame, filtered_df: pd.DataFrame, label: str):
    print(f"\n--- [{label}] Before / After Comparison (written summary) ---")
    print(f"  Row count BEFORE filtering: {len(full_df)}")
    print(f"  Row count AFTER filtering:  {len(filtered_df)}")
    pct_removed = (1 - len(filtered_df) / len(full_df)) * 100 if len(full_df) else 0
    print(f"  Rows excluded from the analysis dataset: "
          f"{len(full_df) - len(filtered_df)} ({pct_removed:.2f}%) -- "
          f"NOTE: excluded only from the FILTERED file; the FULL flagged "
          f"file still contains every one of these rows for audit.")

    for field in REQUIRED_MEDIAN_COMPARISON_FIELDS:
        if field not in full_df.columns:
            continue
        before_median = pd.to_numeric(full_df[field], errors="coerce").median()
        after_median = pd.to_numeric(filtered_df[field], errors="coerce").median()
        if pd.notnull(before_median) and before_median != 0:
            pct_change = (after_median - before_median) / before_median * 100
        else:
            pct_change = float("nan")
        print(f"  {field} median: before={before_median:,.2f}  "
              f"after={after_median:,.2f}  ({pct_change:+.2f}% change)")


# ---------------------------------------------------------------------------
# PIPELINE
# ---------------------------------------------------------------------------
def run_pipeline(input_file: str, label: str, flagged_output: str, filtered_output: str):
    print(f"\n============================ {label.upper()} ============================")
    df = pd.read_csv(input_file, low_memory=False)
    print(f"  Loaded {input_file}: {len(df)} rows, {df.shape[1]} columns")

    print(f"\n--- [{label}] Tier 2: IQR Outlier Detection ---")
    for field, tier1_col in IQR_FIELDS.items():
        df = flag_iqr_outliers(df, field, tier1_col, label)

    df = combine_outlier_flags(df, label)

    # FULL flagged dataset -- nothing removed
    df.to_csv(flagged_output, index=False)
    print(f"\n  Saved FULL flagged dataset -> {flagged_output} ({len(df)} rows)")

    # FILTERED analysis dataset -- excludes any_outlier_flag rows
    filtered = df[~df["any_outlier_flag"]].copy()
    filtered.to_csv(filtered_output, index=False)
    print(f"  Saved FILTERED analysis dataset -> {filtered_output} ({len(filtered)} rows)")

    print_before_after_comparison(df, filtered, label)

    return df, filtered


def main():
    run_pipeline(SOLD_INPUT_FILE, "Sold", SOLD_FLAGGED_FILE, SOLD_FILTERED_FILE)
    run_pipeline(LISTING_INPUT_FILE, "Listing", LISTING_FLAGGED_FILE, LISTING_FILTERED_FILE)
    print("\nDone.")


if __name__ == "__main__":
    main()
