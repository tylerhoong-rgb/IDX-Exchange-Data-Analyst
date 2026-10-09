"""
trim_for_tableau.py

Weeks 8-12 prep: trims the Week 7 Flagged datasets down to only the
columns the required market_analysis.twbx / competitive_analysis.twbx
dashboards (plus the "own design" dashboards and the 1-page report) can
actually use, and consolidates the audit-only flag columns into three
clean boolean filters. This is a VIEW for Tableau, not a change to the
pipeline -- the full Flagged/Cleaned files from earlier weeks are
untouched and remain the audit trail.

IMPORTANT: this reads/writes CSV, not Excel. Loading either of your two
.xlsx Flagged files took 260-290 seconds each in testing -- that's the
Excel format itself being slow at ~400-550K rows, independent of column
count. Trimming columns won't fix that if you keep saving as .xlsx.
Tableau also reads CSV natively and faster than Excel, and has no reason
to prefer .xlsx here. Recommendation: work in CSV (or let Tableau build
a .hyper extract from it) from here on.

Columns kept, and why:
  Identity:      ListingKey
  Dates:         CloseDate, ListingContractDate, PurchaseContractDate, yr_mo
  Geography:     City, CountyOrParish, PostalCode, Latitude, Longitude
  Property:      PropertySubType, ClosePrice, ListPrice, OriginalListPrice,
                 LivingArea, DaysOnMarket, BedroomsTotal,
                 BathroomsTotalInteger, YearBuilt, LotSizeAcres
  Metrics:       close_to_original_list_ratio, price_per_sqft,
                 listing_to_contract_days, contract_to_close_days
  Competitive:   ListAgentFullName, ListOfficeName, BuyerOfficeName
  Economic:      rate_30yr_fixed
  Quality flags: any_outlier_flag, bad_coordinates_flag (new, see below),
                 date_issue_flag (new, see below), duplicate_listing_key_flag

Columns dropped, and why:
  - SchoolDistrict: confirmed 100% null in your uploaded files (the Week 6
    enrichment never actually populated it -- still needs geopandas +
    data.ca.gov network access). Zero value at 100% null; dropped.
  - price_ratio: confirmed byte-for-byte identical to
    close_to_original_list_ratio in your data (same formula). Kept the
    name that matches the handbook's dashboard wording, dropped the alias.
  - days_on_market, year, month: days_on_market is a byte-for-byte
    duplicate of DaysOnMarket; year/month are redundant with
    CloseDate/yr_mo, which Tableau can already break down by year/month
    natively via its date hierarchy.
  - ListAgentFirstName, ListAgentLastName, CoListAgentFirstName,
    CoListAgentLastName: ListAgentFullName alone is sufficient for the
    "Top 100 listing agents" dashboard; co-listing agent isn't part of
    any required dashboard. (These stay in the full Cleaned/Flagged
    files upstream -- this is a Tableau-view trim, not a pipeline change.)
  - ElementarySchool/MiddleOrJuniorSchool/HighSchool/HighSchoolDistrict,
    Flooring, ViewYN, PoolPrivateYN, AssociationFee(Frequency),
    AttachedGarageYN, ParkingTotal, SubdivisionName,
    ContractStatusChangeDate, StateOrProvince (always "CA"), MlsStatus,
    FireplaceYN, Stories, Levels, LotSizeArea, LotSizeSquareFeet (both
    redundant with LotSizeAcres), MainLevelBedrooms, NewConstructionYN,
    GarageSpaces, latfilled/lonfilled (low-coverage, uncertain
    provenance -- see Week 6 notes), ListingId (redundant with
    ListingKey), UnparsedAddress (heavy text field, not needed once
    dashboards work at city/county/zip level), PropertyType (constant
    "Residential" across every row by construction -- filtering on it
    accomplishes nothing), year_month (Period object, redundant with the
    yr_mo string column): none of these feed a required or reasonably
    inferred dashboard. All still exist in the upstream Cleaned/Flagged
    files if you need them.
  - The 6 invalid_*_flag + 5 outlier_*_flag columns: already unioned into
    any_outlier_flag by week7.py. Keeping both the union AND every
    individual input column was redundant for a Tableau filter field.
  - The 4 geographic flags (missing/zero/longitude_positive/implausible
    _coordinates_flag): consolidated into one new bad_coordinates_flag
    (= any of the four) -- one clean filter to exclude untrustworthy map
    points from the zip-code heat maps, instead of four.
  - The 3 date-consistency flags (listing_after_close/purchase_after_close
    /negative_timeline): consolidated into one new date_issue_flag (= any
    of the three) for the same reason.

Input:
    CRMLSSold_Residential_Flagged.csv
    CRMLSListing_Residential_Flagged.csv
    (or the .xlsx equivalents -- set USE_EXCEL_INPUT = True below)

Output:
    CRMLSSold_Residential_Tableau.csv
    CRMLSListing_Residential_Tableau.csv
"""

import os
import pandas as pd

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
INPUT_DIR = "Week7 Output"
OUTPUT_DIR = "Final"
USE_EXCEL_INPUT = True # set True only if you don't have the CSV versions

SOLD_INPUT = os.path.join(
    INPUT_DIR, "CRMLSSold_Residential_Flagged." + ("xlsx" if USE_EXCEL_INPUT else "csv")
)
LISTING_INPUT = os.path.join(
    INPUT_DIR, "CRMLSListing_Residential_Flagged." + ("xlsx" if USE_EXCEL_INPUT else "csv")
)

SOLD_OUTPUT = os.path.join(OUTPUT_DIR, "CRMLSSold_Residential_Tableau.csv")
LISTING_OUTPUT = os.path.join(OUTPUT_DIR, "CRMLSListing_Residential_Tableau.csv")

KEEP_COLUMNS = [
    "ListingKey",
    "CloseDate", "ListingContractDate", "PurchaseContractDate", "yr_mo",
    "City", "CountyOrParish", "PostalCode", "Latitude", "Longitude",
    "PropertySubType", "ClosePrice", "ListPrice", "OriginalListPrice",
    "LivingArea", "DaysOnMarket", "BedroomsTotal", "BathroomsTotalInteger",
    "YearBuilt", "LotSizeAcres",
    "close_to_original_list_ratio", "price_per_sqft",
    "listing_to_contract_days", "contract_to_close_days",
    "ListAgentFullName", "ListOfficeName", "BuyerOfficeName",
    "rate_30yr_fixed",
    "any_outlier_flag", "duplicate_listing_key_flag",
]

GEO_FLAG_SOURCES = ["missing_coordinates_flag", "zero_coordinates_flag",
                     "longitude_positive_flag", "implausible_coordinates_flag"]
DATE_FLAG_SOURCES = ["listing_after_close_flag", "purchase_after_close_flag",
                      "negative_timeline_flag"]


def trim(input_path: str, label: str, output_path: str):
    print(f"\n============================ {label.upper()} ============================")
    read_fn = pd.read_excel if input_path.endswith(".xlsx") else pd.read_csv
    df = read_fn(input_path, low_memory=False) if not input_path.endswith(".xlsx") else read_fn(input_path)
    print(f"  Loaded {input_path}: {len(df)} rows, {df.shape[1]} columns")

    # Consolidate the 4 geo flags into 1, the 3 date flags into 1
    geo_present = [c for c in GEO_FLAG_SOURCES if c in df.columns]
    date_present = [c for c in DATE_FLAG_SOURCES if c in df.columns]
    df["bad_coordinates_flag"] = df[geo_present].any(axis=1) if geo_present else False
    df["date_issue_flag"] = df[date_present].any(axis=1) if date_present else False
    print(f"  bad_coordinates_flag (from {geo_present}): {int(df['bad_coordinates_flag'].sum())} rows")
    print(f"  date_issue_flag (from {date_present}): {int(df['date_issue_flag'].sum())} rows")

    keep = [c for c in KEEP_COLUMNS + ["bad_coordinates_flag", "date_issue_flag"] if c in df.columns]
    missing = [c for c in KEEP_COLUMNS if c not in df.columns]
    if missing:
        print(f"  [WARNING] expected column(s) not found, skipped: {missing}")

    trimmed = df[keep].copy()
    trimmed.to_csv(output_path, index=False)

    print(f"  Columns: {df.shape[1]} -> {trimmed.shape[1]}")
    print(f"  Saved -> {output_path}")
    return trimmed


def main():
    trim(SOLD_INPUT, "Sold", SOLD_OUTPUT)
    trim(LISTING_INPUT, "Listing", LISTING_OUTPUT)
    print("\nDone.")


if __name__ == "__main__":
    main()
