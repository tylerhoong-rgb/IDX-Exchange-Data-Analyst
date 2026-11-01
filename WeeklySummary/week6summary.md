# Week 6 Summary: Feature Engineering and Market Metrics
## 1. Datasets processed

| Dataset | Rows | Columns in | Geocoded rows | Matched to school district |
|---|---|---|---|---|
| Sold (Residential) | 414,063 | 71 | 398,088 | 397,909 (99.95%) |
| Listing (Residential) | 547,162 | 66 | 466,851 | 466,445 (99.9%) |

## 2.Engineered metrics
 All seven metrics plus `SchoolDistrict` are created in both datasets.

| Metric | Formula | Sold non-null | Listing non-null |
|---|---|---|---|
| `price_ratio` | ClosePrice / OriginalListPrice | 413,302 | 136,891 |
| `close_to_original_list_ratio` | ClosePrice / OriginalListPrice | 413,302 | 136,891 |
| `price_per_sqft` | ClosePrice / LivingArea | 413,677 | 137,545 |
| `days_on_market` | DaysOnMarket (raw field) | all | all |
| `year`, `month`, `yr_mo` | Derived from CloseDate | 414,063 | 159,066 |
| `listing_to_contract_days` | PurchaseContractDate - ListingContractDate | 413,867 | 261,486 |
| `contract_to_close_days` | CloseDate - PurchaseContractDate | 413,868 | 159,035 |

Notes:
- The Listing file includes active and pending listings, so close-based metrics (`price_ratio`, `price_per_sqft`, `yr_mo`, `contract_to_close_days`) are only populated for the roughly 159K closed records.
- Extreme price ratios (outside 0.1 to 3.0) were flagged: 926 rows in Sold and 257 in Listing. They stay in the data but are excluded from the ratio statistics in the segment tables.

## 3. Sample output (Sold, new columns populated)

| ListingKey | CloseDate | ClosePrice | OriginalListPrice | LivingArea | price_ratio | price_per_sqft | days_on_market | yr_mo | listing_to_contract_days | contract_to_close_days | SchoolDistrict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 551985747 | 2024-01-26 | 240,000 | 499,000 | 1,140 | 0.481 | 210.53 | 777 | 2024-01 | 777 | 65 | n/a |
| 522107581 | 2024-01-05 | 815,000 | 759,900 | 1,974 | 1.073 | 412.87 | 33 | 2024-01 | 114 | 919 | n/a |
| 510919001 | 2024-01-05 | 810,000 | 739,900 | 1,974 | 1.095 | 410.33 | 228 | 2024-01 | 255 | 778 | n/a |
| 1075037759 | 2024-01-29 | 1,890,500 | 1,890,500 | 3,194 | 1.000 | 591.89 | 0 | 2024-01 | 0 | 0 | Los Angeles Unified |
| 1067652762 | 2024-01-02 | 2,100,000 | 2,100,000 | 3,736 | 1.000 | 562.10 | 0 | 2024-01 | 0 | 48 | San Luis Coastal Unified |

(`close_to_original_list_ratio` equals `price_ratio` in every row; `year` and `month` are also populated but omitted here for width.)

## 4. Segment summary tables (Sold)

### By PropertyType

All Sold records are `Residential`, so this is a single group.

| PropertyType | Records | Median close price | Median price ratio | Median $/sqft | Median DOM |
|---|---|---|---|---|---|
| Residential | 414,063 | $823,000 | 0.996 | $537 | 18 |

### By PropertySubType (top 5 of 21)

| PropertySubType | Records | Median close price | Median price ratio | Median $/sqft | Median DOM | Median list-to-contract days |
|---|---|---|---|---|---|---|
| SingleFamilyResidence | 309,742 | $894,000 | 1.000 | $533 | 17 | 23 |
| Condominium | 68,476 | $628,000 | 0.986 | $565 | 24 | 29 |
| Townhouse | 24,285 | $805,000 | 1.000 | $562 | 17 | 21 |
| ManufacturedOnLand | 5,343 | $324,000 | 0.970 | $226 | 30 | 39 |
| Duplex | 2,263 | $915,000 | 0.983 | $545 | 21 | 31 |

### By CountyOrParish (top 5 of 63)

| County | Records | Median close price | Median price ratio | Median $/sqft | Median DOM | Median contract-to-close days |
|---|---|---|---|---|---|---|
| Los Angeles | 102,907 | $900,000 | 1.000 | $608 | 19 | 30 |
| Riverside | 57,380 | $600,000 | 0.986 | $321 | 30 | 29 |
| San Diego | 51,153 | $899,000 | 0.992 | $591 | 15 | 26 |
| Orange | 46,605 | $1,175,000 | 0.994 | $673 | 14 | 29 |
| San Bernardino | 38,589 | $530,000 | 0.992 | $332 | 25 | 32 |

### By ListOfficeName (competitive intelligence, top 5 of 18,673)

| List office | Records | Median close price | Median price ratio | Median DOM |
|---|---|---|---|---|
| Compass | 29,109 | $1,350,000 | 1.000 | 14 |
| Coldwell Banker Realty | 18,692 | $1,195,000 | 0.999 | 16 |
| Keller Williams Realty | 8,121 | $870,000 | 1.000 | 15 |
| First Team Real Estate | 5,795 | $960,000 | 1.000 | 13 |
| Berkshire Hathaway HomeServices California Properties | 5,476 | $950,000 | 0.984 | 23 |

### By BuyerOfficeName (top 5 of 21,262)

| Buyer office | Records | Median close price | Median price ratio | Median DOM |
|---|---|---|---|---|
| Compass | 27,183 | $1,325,000 | 1.000 | 14 |
| Coldwell Banker Realty | 14,959 | $1,195,000 | 0.996 | 16 |
| NONMEMBER MRML | 8,836 | $504,099 | 0.986 | 26 |
| (missing) | 6,743 | $1,090,000 | 1.000 | 15 |
| Keller Williams Realty | 6,369 | $835,000 | 0.995 | 17 |

The same tables for `MLSAreaMajor` and for the Listing dataset are saved as CSVs in `Week6 Output/` (`Sold_segment_summary_<column>.csv` and `Listing_segment_summary_<column>.csv`).

## 5. What the segments show

- **Negotiation strength differs by property type.** Single-family homes and townhouses typically close at 100% of original list price (median 1.000). Condos close slightly under (0.986), and manufactured homes show the most buyer leverage (0.970).
- **Condos and manufactured homes sell slower.** Median days on market is 24 for condos and 30 for manufactured homes, versus 17 for single-family and townhouses.
- **Regional markets move at different speeds.** Orange (14 days) and San Diego (15 days) are the fastest of the top five counties. Riverside is slowest at 30 days and also has the lowest median price ratio (0.986), which suggests more buyer negotiating room there.
- **Price levels vary widely.** Median close price ranges from $530K in San Bernardino to $1.175M in Orange.
- **Compass leads on volume on both sides.** It has about 29K list-side and 27K buyer-side closings, at a high price point (about $1.3M median) and fast sales (14 days).
- **The "NONMEMBER MRML" buyer group is distinct.** It accounts for 8,836 closings at a $504K median, a 0.986 price ratio, and 26 days on market, a lower-priced and slower profile than the major brokerages.
- **Mean vs. median.** Overall the mean price ratio (0.989) sits slightly below the median (0.996), which is why the summaries report both after removing extreme ratios.

## 6. Data quality notes

- **Odd date intervals in some rows.** In the sample, rows 2 and 3 show `contract_to_close_days` of 919 and 778 days, and row 1 shows `listing_to_contract_days` of 777. These suggest stale or re-used contract dates (for example, a prior failed contract or relisting) rather than true timelines. Consider filtering negative or very large values (for example, above 365 days) before charting these two fields in Tableau.
- **MLSAreaMajor is weak for geography.** In Sold, 55,359 records (13%) have a blank value and another 43,426 are "699 - Not Defined". `CountyOrParish` is the more reliable geographic dimension.
- **Buyer office is mostly blank for Listing records.** 397,275 of 547,162 Listing rows have no `BuyerOfficeName` because most are not closed. That is expected; use the Sold dataset for buyer-side analysis.
- **Close-based Listing statistics describe closed records only.** Columns such as `ClosePrice_median` in the Listing segment tables ignore active listings, even though `record_count` includes them.
- **School district match rate is effectively complete.** Unmatched rows are almost entirely records without usable latitude/longitude (about 16K Sold and 80K Listing rows have no coordinates).