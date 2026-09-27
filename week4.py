"""
Takes the Residential-filtered Sold and Listing datasets and produces analysis-ready datasets by:

  1. Converting date fields to real datetime dtype (CloseDate,
     PurchaseContractDate, ListingContractDate, ContractStatusChangeDate).
  2. Dropping columns that are redundant or not useful for market
     analytics (agent contact info, duplicate ID/address columns,
     source-system metadata) -- see DROP_COLUMNS below for the list and
     the reasoning in drop_redundant_columns(). ListOfficeName and
     BuyerOfficeName are deliberately KEPT (not dropped) even though
     they aren't used for pricing analysis, because Week 6 segment
     analysis needs them for competitive intelligence and should be
     able to read this script's output as its only input.
  3. Ensuring numeric fields are properly typed (coerced to numeric,
     invalid strings become NaN rather than silently breaking dtype).
  4. FLAGGING (not silently deleting) invalid numeric values so the
     underlying rows stay available for audit:
       - invalid_close_price_flag   (ClosePrice <= 0)
       - invalid_living_area_flag   (LivingArea <= 0)
       - invalid_dom_flag           (DaysOnMarket < 0)
       - invalid_bedrooms_flag      (BedroomsTotal < 0)
       - invalid_bathrooms_flag     (BathroomsTotalInteger < 0)
       - invalid_numeric_flag       (any of the above)
  5. Date consistency flags:
       - listing_after_close_flag   (ListingContractDate > CloseDate)
       - purchase_after_close_flag  (PurchaseContractDate > CloseDate)
       - negative_timeline_flag     (ListingContractDate > PurchaseContractDate)
  6. Geographic data quality flags:
       - missing_coordinates_flag   (Latitude or Longitude is null)
       - zero_coordinates_flag      (Latitude == 0 or Longitude == 0)
       - longitude_positive_flag    (Longitude > 0 -- should be negative in CA)
       - implausible_coordinates_flag (outside a CA bounding box)

Rows are NEVER silently dropped for invalid values or bad dates/geo
everything is flagged so downstream analysis can decide whether to
exclude, and reviewers can audit exactly what was flagged and why.

Input:
    CRMLSSold_Residential_Filtered.csv
    CRMLSListing_Residential_Filtered.csv

Output:
    CRMLSSold_Residential_Cleaned.csv
    CRMLSListing_Residential_Cleaned.csv
"""

import os
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
INPUT_DIR = "Week3 Output"
OUTPUT_DIR = "Week4-5 Output"

SOLD_INPUT_FILE = os.path.join(INPUT_DIR, "CRMLSSold_Residential_WithRates.csv")
LISTING_INPUT_FILE = os.path.join(INPUT_DIR, "CRMLSListing_Residential_WithRates.csv")

SOLD_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "CRMLSSold_Residential_Cleaned.csv")
LISTING_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "CRMLSListing_Residential_Cleaned.csv")

DATE_FIELDS = ["CloseDate", "PurchaseContractDate", "ListingContractDate",
               "ContractStatusChangeDate"]

NUMERIC_FIELDS = [
    "ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea",
    "LotSizeAcres", "LotSizeArea", "LotSizeSquareFeet", "BedroomsTotal",
    "BathroomsTotalInteger", "DaysOnMarket", "YearBuilt", "Latitude",
    "Longitude", "AssociationFee", "ParkingTotal", "GarageSpaces",
    "Stories", "MainLevelBedrooms",
]

# Columns dropped as redundant / not useful for market analytics.
# Reasoning noted inline; every dropped column falls into one of:
#   (a) agent/office contact & compensation info -- not analytical
#   (b) a duplicate of another column already retained
#   (c) source-system bookkeeping metadata
DROP_COLUMNS = {
    # (a) agent / office contact & compensation info
    "ListAgentEmail": "agent contact info, not needed for market analytics",
    "ListAgentFirstName": "agent contact info",
    "ListAgentLastName": "agent contact info",
    "ListAgentFullName": "agent contact info",
    "CoListAgentFirstName": "agent contact info",
    "CoListAgentLastName": "agent contact info",
    "BuyerAgentMlsId": "agent identifier, not needed for market analytics",
    "BuyerAgentFirstName": "agent contact info",
    "BuyerAgentLastName": "agent contact info",
    # NOTE: ListOfficeName / BuyerOfficeName are intentionally NOT dropped
    # here even though they aren't used for pricing/market-trend analysis.
    # Week 6 segment analysis needs them for competitive intelligence
    # (office-level performance), and keeping the Week 4-5 output as the
    # single source of truth for Week 6 avoids that script having to read
    # back further upstream than its immediate input.
    "BuyerOfficeName.1": "duplicate of BuyerOfficeName (raw export had duplicate header)",
    "CoListOfficeName": "office info, not needed for market analytics",
    "BuyerOfficeAOR": "office board code, not needed for market analytics",
    "BuyerAgentAOR": "agent board code, not needed for market analytics",
    "ListAgentAOR": "agent board code, not needed for market analytics",
    "BuyerAgencyCompensationType": "commission info, not needed for market analytics",
    "BuyerAgencyCompensation": "commission info, not needed for market analytics",
    # (b) duplicates of a retained column
    "ListingKeyNumeric": "duplicate of ListingKey in numeric form",
    "StreetNumberNumeric": "redundant, derivable from UnparsedAddress",
    "UnparsedAddress.1": "duplicate of UnparsedAddress (raw export had duplicate header)",
    # (c) source-system bookkeeping metadata
    "OriginatingSystemName": "constant source-system metadata, not analytical",
    "OriginatingSystemSubName": "constant source-system metadata, not analytical",
}

# CA bounding box used for the "implausible coordinates" geographic check
CA_LAT_MIN, CA_LAT_MAX = 32.0, 42.5
CA_LON_MIN, CA_LON_MAX = -125.0, -113.5


# ---------------------------------------------------------------------------
# STEP 1 - Convert date fields to datetime
# ---------------------------------------------------------------------------
def convert_dates(df: pd.DataFrame, label: str) -> pd.DataFrame:
    df = df.copy()
    print(f"\n--- [{label}] Date Field Conversion ---")
    for col in DATE_FIELDS:
        if col not in df.columns:
            print(f"  [SKIP] {col} not present in {label}")
            continue
        before_dtype = df[col].dtype
        df[col] = pd.to_datetime(df[col], errors="coerce")
        unparseable = df[col].isnull().sum()
        print(f"  {col}: {before_dtype} -> {df[col].dtype} "
              f"({unparseable} null/unparseable after conversion)")
    return df


# ---------------------------------------------------------------------------
# STEP 2 - Remove unnecessary or redundant columns
# ---------------------------------------------------------------------------
def drop_redundant_columns(df: pd.DataFrame, label: str) -> pd.DataFrame:
    df = df.copy()
    present = [c for c in DROP_COLUMNS if c in df.columns]
    print(f"\n--- [{label}] Redundant Column Removal ---")
    print(f"  Columns before: {df.shape[1]}")
    for c in present:
        print(f"  Dropping '{c}' -- {DROP_COLUMNS[c]}")
    df = df.drop(columns=present)
    print(f"  Columns after: {df.shape[1]}")
    return df


# ---------------------------------------------------------------------------
# STEP 3 - Ensure numeric fields are properly typed
# ---------------------------------------------------------------------------
def enforce_numeric_types(df: pd.DataFrame, label: str) -> pd.DataFrame:
    df = df.copy()
    print(f"\n--- [{label}] Numeric Type Enforcement ---")
    for col in NUMERIC_FIELDS:
        if col not in df.columns:
            continue
        before_dtype = df[col].dtype
        before_non_null = df[col].notnull().sum()
        df[col] = pd.to_numeric(df[col], errors="coerce")
        after_non_null = df[col].notnull().sum()
        newly_nulled = before_non_null - after_non_null
        print(f"  {col}: {before_dtype} -> {df[col].dtype} "
              f"({newly_nulled} values could not be coerced and became NaN)")
    return df


# ---------------------------------------------------------------------------
# STEP 4 - Missing value handling decisions
# ---------------------------------------------------------------------------
def handle_missing_values(df: pd.DataFrame, label: str) -> pd.DataFrame:
    """We do NOT impute core numeric/market fields (ClosePrice, LivingArea,
    etc.) -- fabricating values would bias downstream analysis. Nulls in
    those fields are left as NaN and are fully visible in the null-count
    summary below. The only transformation here is on Y/N boolean-style
    fields, where a null is treated as 'not specified' (kept as NaN, not
    coerced to False) to avoid silently asserting a feature is absent."""
    print(f"\n--- [{label}] Missing Value Handling ---")
    print("  Decision: no imputation of numeric/market fields (would bias "
          "analysis). Nulls are retained and reported below.")
    null_summary = df.isnull().sum().sort_values(ascending=False)
    null_summary = null_summary[null_summary > 0]
    print(f"  {len(null_summary)} columns contain at least one null value "
          f"(see null-count summary in the printed report).")
    return df


# ---------------------------------------------------------------------------
# STEP 5 - Flag invalid numeric values (not removed, flagged for audit)
# ---------------------------------------------------------------------------
def flag_invalid_numeric_values(df: pd.DataFrame, label: str) -> pd.DataFrame:
    df = df.copy()
    print(f"\n--- [{label}] Invalid Numeric Value Flags ---")

    df["invalid_close_price_flag"] = df.get("ClosePrice") <= 0 if "ClosePrice" in df.columns else False
    df["invalid_living_area_flag"] = df.get("LivingArea") <= 0 if "LivingArea" in df.columns else False
    df["invalid_dom_flag"] = df.get("DaysOnMarket") < 0 if "DaysOnMarket" in df.columns else False
    df["invalid_bedrooms_flag"] = df.get("BedroomsTotal") < 0 if "BedroomsTotal" in df.columns else False
    df["invalid_bathrooms_flag"] = df.get("BathroomsTotalInteger") < 0 if "BathroomsTotalInteger" in df.columns else False

    flag_cols = ["invalid_close_price_flag", "invalid_living_area_flag", "invalid_dom_flag",
                 "invalid_bedrooms_flag", "invalid_bathrooms_flag"]
    df[flag_cols] = df[flag_cols].fillna(False)
    df["invalid_numeric_flag"] = df[flag_cols].any(axis=1)

    for col in flag_cols + ["invalid_numeric_flag"]:
        print(f"  {col}: {int(df[col].sum())} rows flagged")

    return df


# ---------------------------------------------------------------------------
# STEP 6 - Date consistency flags
# ---------------------------------------------------------------------------
def flag_date_consistency(df: pd.DataFrame, label: str) -> pd.DataFrame:
    df = df.copy()
    print(f"\n--- [{label}] Date Consistency Flags ---")

    has_lc = "ListingContractDate" in df.columns
    has_pc = "PurchaseContractDate" in df.columns
    has_cd = "CloseDate" in df.columns

    df["listing_after_close_flag"] = (
        (df["ListingContractDate"] > df["CloseDate"]) if has_lc and has_cd else False
    )
    df["purchase_after_close_flag"] = (
        (df["PurchaseContractDate"] > df["CloseDate"]) if has_pc and has_cd else False
    )
    df["negative_timeline_flag"] = (
        (df["ListingContractDate"] > df["PurchaseContractDate"]) if has_lc and has_pc else False
    )

    for col in ["listing_after_close_flag", "purchase_after_close_flag", "negative_timeline_flag"]:
        df[col] = df[col].fillna(False)
        print(f"  {col}: {int(df[col].sum())} rows flagged")

    return df


# ---------------------------------------------------------------------------
# STEP 7 - Geographic data quality flags
# ---------------------------------------------------------------------------
def flag_geographic_quality(df: pd.DataFrame, label: str) -> pd.DataFrame:
    df = df.copy()
    print(f"\n--- [{label}] Geographic Data Quality ---")

    has_geo = "Latitude" in df.columns and "Longitude" in df.columns
    if not has_geo:
        print("  [SKIP] Latitude/Longitude not present.")
        return df

    lat, lon = df["Latitude"], df["Longitude"]

    df["missing_coordinates_flag"] = lat.isnull() | lon.isnull()
    df["zero_coordinates_flag"] = (lat == 0) | (lon == 0)
    df["longitude_positive_flag"] = lon > 0

    has_coords = lat.notnull() & lon.notnull() & ~df["zero_coordinates_flag"]
    out_of_ca_box = (lat < CA_LAT_MIN) | (lat > CA_LAT_MAX) | (lon < CA_LON_MIN) | (lon > CA_LON_MAX)
    df["implausible_coordinates_flag"] = has_coords & out_of_ca_box

    summary = {
        "missing_coordinates_flag": int(df["missing_coordinates_flag"].sum()),
        "zero_coordinates_flag": int(df["zero_coordinates_flag"].sum()),
        "longitude_positive_flag": int(df["longitude_positive_flag"].fillna(False).sum()),
        "implausible_coordinates_flag": int(df["implausible_coordinates_flag"].sum()),
    }
    total = len(df)
    for k, v in summary.items():
        print(f"  {k}: {v} rows flagged ({v / total * 100:.2f}%)")

    any_geo_issue = (df["missing_coordinates_flag"] | df["zero_coordinates_flag"]
                      | df["longitude_positive_flag"].fillna(False) | df["implausible_coordinates_flag"])
    print(f"  TOTAL rows with at least one geographic data quality issue: "
          f"{int(any_geo_issue.sum())} ({any_geo_issue.mean() * 100:.2f}%)")

    return df


# ---------------------------------------------------------------------------
# STEP 8 - Duplicate ListingKey check (data integrity, not geographic)
# ---------------------------------------------------------------------------
def flag_duplicate_listing_keys(df: pd.DataFrame, label: str) -> pd.DataFrame:
    """ListingKey is expected to uniquely identify a record, and later
    pipeline steps (e.g. re-joining ListOfficeName/BuyerOfficeName for
    Week 6 segment analysis) assume it is a safe 1:1 merge key. It is NOT
    always unique in the raw CRMLS export -- some keys repeat multiple
    times with differing field values (observed up to 9x for a single
    key). This is flagged here, at cleaning time, rather than being
    discovered later as a silent row-count inflation bug during a
    downstream merge."""
    df = df.copy()
    print(f"\n--- [{label}] Duplicate ListingKey Check ---")
    if "ListingKey" not in df.columns:
        print("  [SKIP] ListingKey not present.")
        return df

    dupe_mask = df["ListingKey"].duplicated(keep=False)
    df["duplicate_listing_key_flag"] = dupe_mask
    n_dupe_rows = int(dupe_mask.sum())
    n_dupe_keys = df.loc[dupe_mask, "ListingKey"].nunique()
    print(f"  duplicate_listing_key_flag: {n_dupe_rows} rows flagged "
          f"({n_dupe_keys} distinct ListingKey values appear more than once)")
    if n_dupe_rows:
        print("  NOTE: any future merge keyed on ListingKey must "
              "de-duplicate the right-hand table first (keep='first' or "
              "similar), or the merge will silently inflate row counts.")

    return df


# ---------------------------------------------------------------------------
# PIPELINE
# ---------------------------------------------------------------------------
def run_pipeline(input_file: str, label: str, output_file: str) -> pd.DataFrame:
    print(f"\n============================ {label.upper()} ============================")
    df = pd.read_csv(input_file, low_memory=False)
    rows_before = len(df)
    cols_before = df.shape[1]
    print(f"  Loaded {input_file}: {rows_before} rows, {cols_before} columns")

    df = convert_dates(df, label)
    df = drop_redundant_columns(df, label)
    df = enforce_numeric_types(df, label)
    df = handle_missing_values(df, label)
    df = flag_invalid_numeric_values(df, label)
    df = flag_date_consistency(df, label)
    df = flag_geographic_quality(df, label)
    df = flag_duplicate_listing_keys(df, label)

    rows_after = len(df)
    cols_after = df.shape[1]
    print(f"\n--- [{label}] Before/After Summary ---")
    print(f"  Rows:    before={rows_before}  after={rows_after}  "
          f"(no rows dropped -- all issues are flagged, not removed)")
    print(f"  Columns: before={cols_before}  after={cols_after}")

    print(f"\n--- [{label}] Final dtype confirmation (date & numeric fields) ---")
    for col in DATE_FIELDS + NUMERIC_FIELDS:
        if col in df.columns:
            print(f"  {col}: {df[col].dtype}")

    df.to_csv(output_file, index=False)
    print(f"\n  Saved cleaned dataset -> {output_file}")
    return df


def main():
    run_pipeline(SOLD_INPUT_FILE, "Sold", SOLD_OUTPUT_FILE)
    run_pipeline(LISTING_INPUT_FILE, "Listing", LISTING_OUTPUT_FILE)
    print("\nDone.")


if __name__ == "__main__":
    main()