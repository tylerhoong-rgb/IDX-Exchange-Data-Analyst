"""
Takes the analysis-ready Cleaned Sold and Listing datasets (Weeks 4-5) and
engineers the key metrics that power the Tableau dashboards:

    price_ratio                  ClosePrice / OriginalListPrice
    price_per_sqft                ClosePrice / LivingArea
    days_on_market                DaysOnMarket (raw field, carried through)
    year, month, yr_mo             derived from CloseDate
    close_to_original_list_ratio  ClosePrice / OriginalListPrice
    listing_to_contract_days      PurchaseContractDate - ListingContractDate
    contract_to_close_days        CloseDate - PurchaseContractDate

It also attempts to enrich each record with a school district name using
the CA school district boundary polygons (point-in-polygon join on
Latitude/Longitude), and produces segmented summary tables by:
    - PropertyType / PropertySubType
    - CountyOrParish / MLSAreaMajor
    - ListOfficeName / BuyerOfficeName (competitive intelligence)

Input:
    CRMLSSold_Residential_Cleaned.csv
    CRMLSListing_Residential_Cleaned.csv

Output:
    CRMLSSold_Residential_WithMetrics.csv
    CRMLSListing_Residential_WithMetrics.csv
    Sold_segment_summary_<dimension>.csv   (one per segment dimension)
    Listing_segment_summary_<dimension>.csv
"""

import os
import warnings
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
INPUT_DIR = "Week4-5 Output"
OUTPUT_DIR = "Week6 Output"

SOLD_CLEANED_FILE = os.path.join(INPUT_DIR, "CRMLSSold_Residential_Cleaned.csv")
LISTING_CLEANED_FILE = os.path.join(INPUT_DIR, "CRMLSListing_Residential_Cleaned.csv")

SOLD_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "CRMLSSold_Residential_WithMetrics.csv")
LISTING_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "CRMLSListing_Residential_WithMetrics.csv")

# CKAN resource for "California School District Areas 2024-25"
CA_SCHOOL_DISTRICT_RESOURCE_ID = "7dfaf005-58eb-45db-93b1-7aff091b2172"
CKAN_RESOURCE_SHOW_URL = (
    f"https://data.ca.gov/api/3/action/resource_show?id={CA_SCHOOL_DISTRICT_RESOURCE_ID}"
)

SEGMENT_DIMENSIONS = [
    ("PropertyType", "PropertySubType"),
    ("CountyOrParish", "MLSAreaMajor"),
    ("ListOfficeName", "BuyerOfficeName"),
]

REQUIRED_COLUMNS = [
    "ListingKey", "ClosePrice", "OriginalListPrice", "LivingArea", "DaysOnMarket",
    "CloseDate", "PurchaseContractDate", "ListingContractDate",
    "ListOfficeName", "BuyerOfficeName", "PropertyType", "PropertySubType",
    "CountyOrParish", "MLSAreaMajor", "Latitude", "Longitude",
]


# ---------------------------------------------------------------------------
# STEP 0 - Load the Week 4-5 Cleaned file (sole input for this script)
# ---------------------------------------------------------------------------
def load_cleaned(cleaned_file: str, label: str) -> pd.DataFrame:
    date_cols = ["CloseDate", "PurchaseContractDate", "ListingContractDate",
                 "ContractStatusChangeDate"]
    df = pd.read_csv(cleaned_file, low_memory=False, parse_dates=date_cols)
    print(f"  {label}: loaded {cleaned_file} -> {len(df)} rows, {df.shape[1]} columns")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        print(f"  [WARNING] {label}: expected column(s) not found in the Cleaned "
              f"input, some metrics/segments below will be skipped: {missing}")
    return df


# ---------------------------------------------------------------------------
# STEP 1 - Engineer market metrics
# ---------------------------------------------------------------------------
def engineer_metrics(df: pd.DataFrame, label: str) -> pd.DataFrame:
    df = df.copy()
    print(f"\n--- [{label}] Feature Engineering ---")

    # Price Ratio / Close to Original List Ratio (identical formula, both names kept)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = df["ClosePrice"] / df["OriginalListPrice"].replace(0, np.nan)
    df["price_ratio"] = ratio
    df["close_to_original_list_ratio"] = ratio
    extreme_ratio = ((ratio > 3) | (ratio < 0.1)).sum()
    print(f"  price_ratio / close_to_original_list_ratio: "
          f"{df['price_ratio'].notnull().sum()} non-null values "
          f"({extreme_ratio} rows have a ratio outside [0.1, 3.0] -- almost "
          f"always a near-zero or clearly wrong OriginalListPrice rather than "
          f"a real 10x+ price move; use the median, not the mean, when "
          f"summarizing this field, or filter these rows out first)")

    # Price Per Sq Ft
    with np.errstate(divide="ignore", invalid="ignore"):
        df["price_per_sqft"] = df["ClosePrice"] / df["LivingArea"].replace(0, np.nan)
    print(f"  price_per_sqft: {df['price_per_sqft'].notnull().sum()} non-null values")

    # Days on Market (raw field, carried through under the engineered name too)
    df["days_on_market"] = df["DaysOnMarket"]

    # Year / Month / YrMo, derived from CloseDate
    df["year"] = df["CloseDate"].dt.year
    df["month"] = df["CloseDate"].dt.month
    df["yr_mo"] = df["CloseDate"].dt.to_period("M").astype(str)
    print(f"  year/month/yr_mo: {df['yr_mo'].notnull().sum()} non-null values "
          f"(null where CloseDate is null, e.g. active listings)")

    # Listing to Contract Days
    df["listing_to_contract_days"] = (
        df["PurchaseContractDate"] - df["ListingContractDate"]
    ).dt.days
    print(f"  listing_to_contract_days: {df['listing_to_contract_days'].notnull().sum()} non-null values")

    # Contract to Close Days
    df["contract_to_close_days"] = (
        df["CloseDate"] - df["PurchaseContractDate"]
    ).dt.days
    print(f"  contract_to_close_days: {df['contract_to_close_days'].notnull().sum()} non-null values")

    return df


# ---------------------------------------------------------------------------
# STEP 2 - School district enrichment (best-effort, network-dependent)
# ---------------------------------------------------------------------------
def enrich_school_districts(df: pd.DataFrame, label: str) -> pd.DataFrame:
    """Point-in-polygon join of each record's Latitude/Longitude against the
    CA school district boundary polygons published on data.ca.gov. Requires
    geopandas/shapely and network access to data.ca.gov. If either is
    unavailable (as in a locked-down sandbox), this fails gracefully: the
    'SchoolDistrict' column is added as all-null and a warning is printed,
    rather than crashing the whole pipeline."""
    df = df.copy()
    print(f"\n--- [{label}] School District Enrichment ---")
    try:
        import geopandas as gpd
        import requests

        resp = requests.get(CKAN_RESOURCE_SHOW_URL, timeout=15)
        resp.raise_for_status()
        resource_url = resp.json()["result"]["url"]
        print(f"  Resolved school district boundary file -> {resource_url}")

        districts = gpd.read_file(resource_url)

        has_coords = df["Latitude"].notnull() & df["Longitude"].notnull()
        points = gpd.GeoDataFrame(
            df.loc[has_coords, ["ListingKey"]],
            geometry=gpd.points_from_xy(df.loc[has_coords, "Longitude"],
                                         df.loc[has_coords, "Latitude"]),
            crs=districts.crs,
        )
        joined = gpd.sjoin(points, districts, how="left", predicate="within")
        district_name_col = next(
            c for c in districts.columns if "name" in c.lower() and "district" in c.lower()
        )
        df["SchoolDistrict"] = df["ListingKey"].map(
            joined.set_index("ListingKey")[district_name_col]
        )
        matched = df["SchoolDistrict"].notnull().sum()
        print(f"  Matched {matched} / {has_coords.sum()} geocoded rows to a school district")

    except Exception as e:
        df["SchoolDistrict"] = np.nan
        print(f"  [WARNING] School district enrichment skipped -- {type(e).__name__}: {e}")
        print("  'SchoolDistrict' column added as all-null. This typically means "
              "geopandas isn't installed or data.ca.gov isn't reachable from this "
              "environment. Install geopandas + shapely and confirm data.ca.gov "
              "network access to populate this field.")

    return df


# ---------------------------------------------------------------------------
# STEP 3 - Segment analysis
# ---------------------------------------------------------------------------
def segment_summary(df: pd.DataFrame, group_col: str, label: str) -> pd.DataFrame:
    if group_col not in df.columns:
        print(f"  [SKIP] {group_col} not present in {label}")
        return pd.DataFrame()

    agg_cols = {
        "ListingKey": "count",
        "ClosePrice": ["median", "mean"],
        # median, not just mean, for price_ratio -- a handful of records with
        # a tiny/incorrect OriginalListPrice produce extreme ratios (100x+)
        # that badly skew the mean; see the outlier note printed below.
        "price_ratio": ["median", "mean"],
        "price_per_sqft": "mean",
        "days_on_market": "mean",
    }
    agg_cols = {k: v for k, v in agg_cols.items() if k in df.columns}

    summary = df.groupby(group_col, dropna=False).agg(agg_cols)
    summary.columns = ["_".join(c) if isinstance(c, tuple) else c for c in summary.columns]
    summary = summary.rename(columns={"ListingKey_count": "record_count"})
    summary = summary.sort_values("record_count", ascending=False)
    return summary


def run_segment_analysis(df: pd.DataFrame, label: str):
    print(f"\n--- [{label}] Segment Analysis ---")
    for primary, secondary in SEGMENT_DIMENSIONS:
        for col in (primary, secondary):
            summary = segment_summary(df, col, label)
            if summary.empty:
                continue
            out_path = os.path.join(OUTPUT_DIR, f"{label}_segment_summary_{col}.csv")
            summary.to_csv(out_path)
            print(f"  Saved segment summary by '{col}' ({len(summary)} groups) -> {out_path}")
            print(summary.head(5).to_string())
            print()


# ---------------------------------------------------------------------------
# PIPELINE
# ---------------------------------------------------------------------------
def run_pipeline(cleaned_file: str, label: str, output_file: str) -> pd.DataFrame:
    print(f"\n============================ {label.upper()} ============================")
    df = load_cleaned(cleaned_file, label)
    df = engineer_metrics(df, label)
    df = enrich_school_districts(df, label)

    sample_cols = [c for c in [
        "ListingKey", "CloseDate", "ClosePrice", "OriginalListPrice", "LivingArea",
        "price_ratio", "close_to_original_list_ratio", "price_per_sqft",
        "days_on_market", "year", "month", "yr_mo",
        "listing_to_contract_days", "contract_to_close_days", "SchoolDistrict",
    ] if c in df.columns]
    print(f"\n--- [{label}] Sample Output (engineered columns populated) ---")
    sample = df.loc[df["price_ratio"].notnull(), sample_cols].head(5)
    print(sample.to_string(index=False))

    run_segment_analysis(df, label)

    df.to_csv(output_file, index=False)
    print(f"\n  Saved enriched dataset -> {output_file}")
    return df


def main():
    warnings.filterwarnings("ignore")
    run_pipeline(SOLD_CLEANED_FILE, "Sold", SOLD_OUTPUT_FILE)
    run_pipeline(LISTING_CLEANED_FILE, "Listing", LISTING_OUTPUT_FILE)
    print("\nDone.")


if __name__ == "__main__":
    main()