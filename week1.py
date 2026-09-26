

import os
from datetime import date
import pandas as pd


INPUT_DIR = "CSV Files"           
OUTPUT_DIR = "Week1 Output"             
START_YEAR, START_MONTH = 2024, 1   

LISTING_PREFIX = "CRMLSListing"
SOLD_PREFIX = "CRMLSSold"

LISTING_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "CRMLSListing_Residential_Combined.csv")
SOLD_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "CRMLSSold_Residential_Combined.csv")


def most_recently_completed_month(today: date) -> tuple[int, int]:
    """Return last fully completed calendar month for future proofing"""
    first_of_this_month = today.replace(day=1)
    last_day_prev_month = first_of_this_month - pd.Timedelta(days=1)
    return last_day_prev_month.year, last_day_prev_month.month


def month_range(start_year: int, start_month: int, end_year: int, end_month: int):
    """Yield (year, month) tuples from start to end, inclusive."""
    y, m = start_year, start_month
    while (y, m) <= (end_year, end_month):
        yield y, m
        m += 1
        if m > 12:
            m = 1
            y += 1


def build_file_list(prefix: str, months):
    """Build list of file paths for the given prefix and list of (year, month)."""
    files = []
    for y, m in months:
        fname = f"{prefix}{y}{m:02d}.csv"
        fpath = os.path.join(INPUT_DIR, fname)
        files.append(fpath)
    return files


def load_and_concatenate(file_paths, label: str) -> pd.DataFrame:
    """Read each monthly CSV (skipping any that are missing) and concatenate
    them into a single DataFrame, printing row counts along the way."""\
    # may need to edit for CRMLSSold_filled files``
    frames = []
    running_total_before_concat = 0

    for fpath in file_paths:
        if not os.path.exists(fpath):
            filled_path = fpath.replace(".csv", "_filled.csv")
            if os.path.exists(filled_path):
                print(f"  [INFO] {label}: using _filled fallback -> {os.path.basename(filled_path)}")
                fpath = filled_path
            else:
                print(f"  [WARNING] {label}: file not found, skipping -> {fpath}")
                continue
        df = pd.read_csv(fpath, low_memory=False)
        print(f"  Loaded {os.path.basename(fpath)}: {len(df)} rows")
        running_total_before_concat += len(df)
        frames.append(df)

    # Row count before concatenation = sum of rows across all individual
    # monthly files that were successfully loaded.
    print(f"  --> {label} TOTAL rows across all monthly files BEFORE concat: "
          f"{running_total_before_concat}")

    combined = pd.concat(frames, ignore_index=True)

    # Row count after concatenation = rows in the single combined DataFrame.
    # This should equal the "before" total (concat does not drop rows).
    print(f"  --> {label} rows AFTER concat: {len(combined)}")

    return combined


def filter_residential(df: pd.DataFrame, label: str) -> pd.DataFrame:
    """Filter a DataFrame down to PropertyType == 'Residential', printing
    row counts before and after the filter."""
    rows_before_filter = len(df)
    print(f"  {label} rows BEFORE Residential filter: {rows_before_filter}")

    filtered = df[df["PropertyType"] == "Residential"].copy()

    rows_after_filter = len(filtered)
    print(f"  {label} rows AFTER Residential filter: {rows_after_filter}")

    return filtered


def main():
    today = date.today()
    end_year, end_month = most_recently_completed_month(today)
    months = list(month_range(START_YEAR, START_MONTH, end_year, end_month))

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Date range: {START_YEAR}-{START_MONTH:02d} through "
          f"{end_year}-{end_month:02d} ({len(months)} months)\n")


    print("=== Processing LISTING files ===")
    listing_files = build_file_list(LISTING_PREFIX, months)
    listings = load_and_concatenate(listing_files, "Listings")
    listings_residential = filter_residential(listings, "Listings")

    listings_residential.to_csv(LISTING_OUTPUT_FILE, index=False)
    print(f"  Saved -> {LISTING_OUTPUT_FILE}\n")

    print("=== Processing SOLD files ===")
    sold_files = build_file_list(SOLD_PREFIX, months)
    sold = load_and_concatenate(sold_files, "Sold")
    sold_residential = filter_residential(sold, "Sold")

    sold_residential.to_csv(SOLD_OUTPUT_FILE, index=False)
    print(f"  Saved -> {SOLD_OUTPUT_FILE}\n")

    print("Done.")


if __name__ == "__main__":
    main()