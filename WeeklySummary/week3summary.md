Fetching MORTGAGE30US from FRED: https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US
  Fetched 2898 weekly observations (1971-04-02 to 2026-10-08)
  Resampled to 667 monthly averages (1971-04 to 2026-10)

--- Sold dataset ---
  Loaded Week2 Output/CRMLSSold_Residential_Filtered.csv: 414063 rows

--- [Sold] Merge Validation ---
Rows with null rate_30yr_fixed after merge: 0 / 414063
  PASS: no null rate values after merge.
Preview:
 CloseDate year_month  ClosePrice  ListPrice  rate_30yr_fixed
2024-01-26    2024-01    240000.0   295000.0           6.6425
2024-01-05    2024-01    815000.0   759900.0           6.6425
2024-01-05    2024-01    810000.0   770000.0           6.6425
2024-01-30    2024-01    858000.0   858000.0           6.6425
2024-01-29    2024-01   1890500.0  1890500.0           6.6425
--- Listing dataset ---
  Loaded Week2 Output/CRMLSListing_Residential_Filtered.csv: 547162 rows

--- [Listing] Merge Validation ---
Rows with null rate_30yr_fixed after merge: 0 / 547162
  PASS: no null rate values after merge.
Preview:
ListingContractDate year_month  ClosePrice  ListPrice  rate_30yr_fixed
         2024-01-01    2024-01         NaN  1340000.0           6.6425
         2024-01-24    2024-01         NaN  2500000.0           6.6425
         2024-01-12    2024-01         NaN  3150000.0           6.6425
         2024-01-20    2024-01         NaN  3090000.0           6.6425
         2024-01-12    2024-01         NaN 12725000.0           6.6425
