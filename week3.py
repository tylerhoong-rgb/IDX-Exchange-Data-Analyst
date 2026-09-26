"""
1. Fetches the FRED MORTGAGE30US series (30-year fixed mortgage rate,
   weekly, Thursdays) directly from FRED as CSV
2. Resamples it from weekly to monthly averages via a year_month key.
3. Builds a matching year_month key on the combined Sold and Listing
   datasets (off CloseDate and ListingContractDate respectively) and
   left-merges the monthly rate onto both.
4. Validates the merge: reports how many rows have a null
   rate_30yr_fixed after the merge, and why (a null after the merge
   means that row's year_month fell outside the range FRED returned,
   or the source date field itself was null/unparseable -- it is NOT
   caused by the merge logic itself).
5. Saves both enriched datasets as new CSVs.

Input:
    CRMLSSold_Residential_Filtered.csv     (from the Week 2-3 EDA script)
    CRMLSListing_Residential_Filtered.csv  (from the Week 2-3 EDA script)

Output:
    CRMLSSold_Residential_WithRates.csv
    CRMLSListing_Residential_WithRates.csv
"""

import os
import pandas as pd

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
INPUT_DIR = "Week2 Output"
OUTPUT_DIR = "Week3 Output"

SOLD_INPUT_FILE = os.path.join(INPUT_DIR, "CRMLSSold_Residential_Filtered.csv")
LISTING_INPUT_FILE = os.path.join(INPUT_DIR, "CRMLSListing_Residential_Filtered.csv")

SOLD_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "CRMLSSold_Residential_WithRates.csv")
LISTING_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "CRMLSListing_Residential_WithRates.csv")

FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"


# ---------------------------------------------------------------------------
# STEP 1 - Fetch the mortgage rate data from FRED
# ---------------------------------------------------------------------------
def fetch_mortgage_rates() -> pd.DataFrame:
    print(f"Fetching MORTGAGE30US from FRED: {FRED_URL}")
    mortgage = pd.read_csv(FRED_URL, parse_dates=["observation_date"])
    mortgage.columns = ["date", "rate_30yr_fixed"]
    print(f"  Fetched {len(mortgage)} weekly observations "
          f"({mortgage['date'].min().date()} to {mortgage['date'].max().date()})")
    return mortgage


# ---------------------------------------------------------------------------
# STEP 2 - Resample weekly rates to monthly averages
# ---------------------------------------------------------------------------
def resample_to_monthly(mortgage: pd.DataFrame) -> pd.DataFrame:
    mortgage = mortgage.copy()
    mortgage["year_month"] = mortgage["date"].dt.to_period("M")
    mortgage_monthly = (
        mortgage.groupby("year_month")["rate_30yr_fixed"]
        .mean()
        .reset_index()
    )
    print(f"  Resampled to {len(mortgage_monthly)} monthly averages "
          f"({mortgage_monthly['year_month'].min()} to {mortgage_monthly['year_month'].max()})")
    return mortgage_monthly


# ---------------------------------------------------------------------------
# STEP 3 & 4 - Build year_month key on an MLS dataset and merge the rate on
# ---------------------------------------------------------------------------
def enrich_with_rates(df: pd.DataFrame, date_col: str, mortgage_monthly: pd.DataFrame,
                       label: str) -> pd.DataFrame:
    df = df.copy()
    parsed_dates = pd.to_datetime(df[date_col], errors="coerce")
    df["year_month"] = parsed_dates.dt.to_period("M")

    unparseable = parsed_dates.isnull().sum()
    if unparseable:
        print(f"  [WARNING] {label}: {unparseable} rows have a null/unparseable "
              f"{date_col} and therefore no year_month key -> rate will be null "
              f"for those rows after the merge (expected, not a merge bug).")

    enriched = df.merge(mortgage_monthly, on="year_month", how="left")
    return enriched


# ---------------------------------------------------------------------------
# STEP 5 - Validate the merge
# ---------------------------------------------------------------------------
def validate_merge(df: pd.DataFrame, date_col: str, label: str):
    null_rate_count = df["rate_30yr_fixed"].isnull().sum()
    total = len(df)
    print(f"\n--- [{label}] Merge Validation ---")
    print(f"Rows with null rate_30yr_fixed after merge: {null_rate_count} / {total}")

    if null_rate_count:
        # Break down *why* they're null: missing source date vs. year_month
        # outside the range FRED returned.
        missing_date = df[date_col].isnull().sum() if date_col in df.columns else "n/a"
        print(f"  Of these, {missing_date} have a null/unparseable {date_col} "
              f"(source data issue, not a merge issue).")
        out_of_range_months = sorted(
            df.loc[df["rate_30yr_fixed"].isnull() & df["year_month"].notna(), "year_month"]
            .unique()
            .astype(str)
        )
        if out_of_range_months:
            print(f"  {len(out_of_range_months)} distinct year_month value(s) had no "
                  f"matching FRED monthly rate: {out_of_range_months}")
    else:
        print("  PASS: no null rate values after merge.")

    preview_cols = [c for c in [date_col, "year_month", "ClosePrice", "ListPrice",
                                 "rate_30yr_fixed"] if c in df.columns]
    print(f"Preview:\n{df[preview_cols].head().to_string(index=False)}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    mortgage = fetch_mortgage_rates()
    mortgage_monthly = resample_to_monthly(mortgage)

    print("\n--- Sold dataset ---")
    sold = pd.read_csv(SOLD_INPUT_FILE, low_memory=False)
    print(f"  Loaded {SOLD_INPUT_FILE}: {len(sold)} rows")
    sold_with_rates = enrich_with_rates(sold, "CloseDate", mortgage_monthly, "Sold")
    validate_merge(sold_with_rates, "CloseDate", "Sold")
    sold_with_rates.to_csv(SOLD_OUTPUT_FILE, index=False)
    print(f"  Saved -> {SOLD_OUTPUT_FILE}")

    print("\n--- Listing dataset ---")
    listings = pd.read_csv(LISTING_INPUT_FILE, low_memory=False)
    print(f"  Loaded {LISTING_INPUT_FILE}: {len(listings)} rows")
    listings_with_rates = enrich_with_rates(listings, "ListingContractDate", mortgage_monthly, "Listing")
    validate_merge(listings_with_rates, "ListingContractDate", "Listing")
    listings_with_rates.to_csv(LISTING_OUTPUT_FILE, index=False)
    print(f"  Saved -> {LISTING_OUTPUT_FILE}")

    print("\nDone.")


if __name__ == "__main__":
    main()
