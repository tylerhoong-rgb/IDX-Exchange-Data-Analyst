"""
Week 6 - Feature Engineering and Market Metrics

Takes the analysis-ready Cleaned Sold and Listing datasets (Weeks 4-5) and
engineers the key metrics that power the Tableau dashboards:

    price_ratio                   ClosePrice / OriginalListPrice
    price_per_sqft                ClosePrice / LivingArea
    days_on_market                DaysOnMarket (raw field, carried through)
    year, month, yr_mo            derived from CloseDate
    close_to_original_list_ratio  ClosePrice / OriginalListPrice
    listing_to_contract_days      PurchaseContractDate - ListingContractDate
    contract_to_close_days        CloseDate - PurchaseContractDate

It also enriches each record with a school district name using the local
California School District Areas 2024-25 shapefile (point-in-polygon join on
Latitude/Longitude), and produces segmented summary tables by:
    - PropertyType / PropertySubType
    - CountyOrParish / MLSAreaMajor
    - ListOfficeName / BuyerOfficeName (competitive intelligence)

Input:
    Week4-5 Output/CRMLSSold_Residential_Cleaned.csv
    Week4-5 Output/CRMLSListing_Residential_Cleaned.csv
    DistrictAreas2425/DistrictAreas2425.shp (+ .shx .dbf .prj .cpg alongside)

Output (in Week6 Output/):
    CRMLSSold_Residential_WithMetrics.csv
    CRMLSListing_Residential_WithMetrics.csv
    Sold_segment_summary_<column>.csv
    Listing_segment_summary_<column>.csv

Requirements:
    pip install pandas numpy geopandas shapely pyogrio
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

# Local copy of "California School District Areas 2024-25".
# Keep the .shp, .shx, .dbf, .prj and .cpg files together in the same folder.
# If the files sit next to this script, use "DistrictAreas2425.shp" instead.
SCHOOL_DISTRICT_SHP = os.path.join("DistrictAreas2425", "DistrictAreas2425.shp")

# In this shapefile the district name field is "DistrictNa" (shapefile field
# names are truncated to 10 characters). Fallbacks are tried if it differs.
DISTRICT_NAME_COL = "DistrictNa"
DISTRICT_NAME_FALLBACKS = ["DistrictName", "NAME", "FULLNAME", "DISTRICT"]

# Ratios outside this range almost always come from a near-zero / wrong
# OriginalListPrice, not a real price move. They are excluded from the
# price_ratio statistics in the segment summaries (raw values stay in the data).
RATIO_MIN, RATIO_MAX = 0.1, 3.0

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
# STEP 0 - Load the Week 4-5 Cleaned file (sole input for the metrics)
# ---------------------------------------------------------------------------
def load_cleaned(cleaned_file: str, label: str) -> pd.DataFrame:
    date_cols = ["CloseDate", "PurchaseContractDate", "ListingContractDate",
                 "ContractStatusChangeDate"]
    # Only parse date columns that actually exist (avoids a ValueError)
    header = pd.read_csv(cleaned_file, nrows=0).columns
    date_cols = [c for c in date_cols if c in header]

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
    extreme_ratio = ((ratio > RATIO_MAX) | (ratio < RATIO_MIN)).sum()
    print(f"  price_ratio / close_to_original_list_ratio: "
          f"{ratio.notnull().sum()} non-null values "
          f"({extreme_ratio} rows outside [{RATIO_MIN}, {RATIO_MAX}] -- almost "
          f"always a near-zero or clearly wrong OriginalListPrice; these are "
          f"excluded from the ratio statistics in the segment summaries)")

    # Price Per Sq Ft
    with np.errstate(divide="ignore", invalid="ignore"):
        df["price_per_sqft"] = df["ClosePrice"] / df["LivingArea"].replace(0, np.nan)
    print(f"  price_per_sqft: {df['price_per_sqft'].notnull().sum()} non-null values")

    # Days on Market (raw field, carried through under the engineered name too)
    df["days_on_market"] = df["DaysOnMarket"]

    # Year / Month / YrMo, derived from CloseDate. Keep real nulls (not the
    # string "NaT") where CloseDate is missing, e.g. active listings.
    df["year"] = df["CloseDate"].dt.year
    df["month"] = df["CloseDate"].dt.month
    yr_mo = df["CloseDate"].dt.to_period("M").astype(str)
    df["yr_mo"] = yr_mo.where(df["CloseDate"].notnull(), np.nan)
    print(f"  year/month/yr_mo: {df['yr_mo'].notnull().sum()} non-null values "
          f"(null where CloseDate is null)")

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
# STEP 2 - School district enrichment (local shapefile, point-in-polygon)
# ---------------------------------------------------------------------------
_DISTRICTS_CACHE = {}


def load_districts():
    """Read the shapefile once and reuse it for both datasets."""
    if "gdf" not in _DISTRICTS_CACHE:
        import geopandas as gpd

        if not os.path.exists(SCHOOL_DISTRICT_SHP):
            raise FileNotFoundError(f"Shapefile not found: {SCHOOL_DISTRICT_SHP}")
        gdf = gpd.read_file(SCHOOL_DISTRICT_SHP)
        print(f"  Loaded {len(gdf)} district polygons from {SCHOOL_DISTRICT_SHP} "
              f"(CRS: {gdf.crs})")

        name_col = next(
            (c for c in [DISTRICT_NAME_COL] + DISTRICT_NAME_FALLBACKS if c in gdf.columns),
            None,
        )
        if name_col is None:
            raise KeyError(f"No district name column found. Columns: {gdf.columns.tolist()}")
        _DISTRICTS_CACHE["gdf"] = gdf[[name_col, "geometry"]].rename(
            columns={name_col: "SchoolDistrict"}
        )
    return _DISTRICTS_CACHE["gdf"]


def enrich_school_districts(df: pd.DataFrame, label: str) -> pd.DataFrame:
    """Point-in-polygon join of each record's Latitude/Longitude against the
    CA school district polygons. If geopandas or the shapefile is unavailable,
    'SchoolDistrict' is added as all-null and a warning is printed, rather
    than crashing the whole pipeline."""
    df = df.copy()
    print(f"\n--- [{label}] School District Enrichment ---")
    try:
        import geopandas as gpd

        districts = load_districts()

        has_coords = (
            df["Latitude"].notnull() & df["Longitude"].notnull()
            & (df["Latitude"] != 0) & (df["Longitude"] != 0)
        )
        # Points are lat/long (EPSG:4326); reproject to the shapefile's CRS
        # (this file is Web Mercator, so skipping this would match nothing).
        points = gpd.GeoDataFrame(
            index=df.index[has_coords],
            geometry=gpd.points_from_xy(df.loc[has_coords, "Longitude"],
                                         df.loc[has_coords, "Latitude"]),
            crs="EPSG:4326",
        ).to_crs(districts.crs)

        joined = gpd.sjoin(points, districts, how="left", predicate="within")
        # A point on a shared boundary / overlapping polygons can match twice;
        # keep one match per original row (joined's index is df's index).
        joined = joined[~joined.index.duplicated(keep="first")]

        df["SchoolDistrict"] = joined["SchoolDistrict"].reindex(df.index)
        matched = df["SchoolDistrict"].notnull().sum()
        geocoded = int(has_coords.sum())
        pct = 100 * matched / geocoded if geocoded else 0
        print(f"  Matched {matched} / {geocoded} geocoded rows to a school district ({pct:.1f}%)")
        if geocoded and pct < 95:
            print("  [NOTE] Match rate is below 95% -- check for bad coordinates "
                  "(e.g. positive longitudes or points outside California).")

    except Exception as e:
        df["SchoolDistrict"] = np.nan
        print(f"  [WARNING] School district enrichment skipped -- {type(e).__name__}: {e}")
        print("  'SchoolDistrict' column added as all-null. Make sure geopandas, "
              "shapely and pyogrio are installed (pip install geopandas shapely "
              f"pyogrio) and that '{SCHOOL_DISTRICT_SHP}' exists with its .shx/"
              ".dbf/.prj files alongside it.")

    return df


# ---------------------------------------------------------------------------
# STEP 3 - Segment analysis
# ---------------------------------------------------------------------------
def segment_summary(df: pd.DataFrame, group_col: str, label: str) -> pd.DataFrame:
    if group_col not in df.columns:
        print(f"  [SKIP] {group_col} not present in {label}")
        return pd.DataFrame()

    work = df.copy()
    # Ratio statistics use only plausible ratios, so a few rows with a
    # tiny/incorrect OriginalListPrice can't distort the segment mean.
    work["price_ratio_valid"] = work["price_ratio"].where(
        work["price_ratio"].between(RATIO_MIN, RATIO_MAX)
    )

    agg_cols = {
        "ListingKey": "count",
        "ClosePrice": ["median", "mean"],
        "price_ratio_valid": ["median", "mean"],
        "price_per_sqft": ["median", "mean"],
        "days_on_market": ["median", "mean"],
        "listing_to_contract_days": "median",
        "contract_to_close_days": "median",
    }
    agg_cols = {k: v for k, v in agg_cols.items() if k in work.columns}

    summary = work.groupby(group_col, dropna=False).agg(agg_cols)
    summary.columns = ["_".join(c) if isinstance(c, tuple) else c for c in summary.columns]
    summary = summary.rename(columns={
        "ListingKey_count": "record_count",
        "price_ratio_valid_median": "price_ratio_median",
        "price_ratio_valid_mean": "price_ratio_mean",
    })
    summary = summary.sort_values("record_count", ascending=False).round(3)
    return summary


def run_segment_analysis(df: pd.DataFrame, label: str):
    print(f"\n--- [{label}] Segment Analysis ---")
    print(f"  (price_ratio stats exclude ratios outside [{RATIO_MIN}, {RATIO_MAX}])")
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
    populated = df["price_ratio"].notnull() & df["price_per_sqft"].notnull()
    sample = df.loc[populated, sample_cols].head(5)
    print(sample.to_string(index=False))

    run_segment_analysis(df, label)

    df.to_csv(output_file, index=False)
    print(f"\n  Saved enriched dataset -> {output_file}")
    return df


def main():
    warnings.filterwarnings("ignore")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    run_pipeline(SOLD_CLEANED_FILE, "Sold", SOLD_OUTPUT_FILE)
    run_pipeline(LISTING_CLEANED_FILE, "Listing", LISTING_OUTPUT_FILE)
    print("\nDone.")


if __name__ == "__main__":
    main()