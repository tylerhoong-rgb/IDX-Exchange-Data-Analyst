# Weeks 4-5 Summary: Data Cleaning and Preparation
## 1. Before / after row and column counts

| Dataset | Rows before | Rows after | Columns before | Columns after dropping | Columns in final file |
|---|---|---|---|---|---|
| Sold | 414,063 | 414,063 | 71 | 57 | 71 |
| Listing | 547,162 | 547,162 | 64 | 52 | 66 |

- **No rows were removed.** Problem records are flagged, not deleted, so every row stays available for audit. The Week 6 scripts will load the same 414,063 and 547,162 rows.
- The final column count is the retained columns plus 14 flag columns (5 invalid-value flags plus the combined `invalid_numeric_flag`, 3 date flags, 4 geographic flags and `duplicate_listing_key_flag`).

## 2. Date conversion

All four fields were converted to `datetime64`: `CloseDate`, `PurchaseContractDate`, `ListingContractDate`, `ContractStatusChangeDate`.

| Field | Sold nulls | Listing nulls |
|---|---|---|
| CloseDate | 0 | 388,096 |
| PurchaseContractDate | 195 | 285,676 |
| ListingContractDate | 1 | 0 |
| ContractStatusChangeDate | 589 | 6,311 |

The conversion did not create new nulls. These blanks were already in the raw data. The large Listing counts are expected, because most listing records are active or pending and have no close or contract date yet. The 159,066 non-null Listing close dates match the number of closed records seen in Week 6.

## 3. Redundant column removal

| Dataset | Columns dropped |
|---|---|
| Sold | 14 (71 to 57) |
| Listing | 12 (64 to 52) |

Columns were dropped for three reasons:
- **Agent contact info and identifiers:** `ListAgentEmail`, `BuyerAgentMlsId`, `BuyerAgentFirstName`, `BuyerAgentLastName`.
- **Office/board codes, commission fields and source-system metadata:** `CoListOfficeName`, `BuyerOfficeAOR`, `BuyerAgentAOR`, `ListAgentAOR`, `BuyerAgencyCompensationType`, `BuyerAgencyCompensation`, `OriginatingSystemName`, `OriginatingSystemSubName`. The last two apply to Sold only, as do `BuyerAgentAOR` and `ListAgentAOR`.
- **Duplicates of columns already kept:** `ListingKeyNumeric`, `StreetNumberNumeric`, and for Listing only `BuyerOfficeName.1` and `UnparsedAddress.1` (the raw export had duplicate headers).

## 4. Missing values

| Dataset | Columns with at least one null |
|---|---|
| Sold | 45 |
| Listing | 41 |

Core market fields (ClosePrice, LivingArea and so on) are left as null rather than filled, because invented values would bias the analysis. Boolean-style fields are not coerced to False, since a blank means "not specified", not "absent".

## 5. Numeric typing

Numeric fields were confirmed as numeric in both datasets: `ClosePrice`, `ListPrice`, `OriginalListPrice`, `LivingArea`, the lot-size fields, `BedroomsTotal`, `BathroomsTotalInteger`, `YearBuilt`, `Latitude`, `Longitude`, `AssociationFee`, `ParkingTotal`, `GarageSpaces`, `Stories` and `MainLevelBedrooms` are `float64`; `DaysOnMarket` is `int64`.

## 6. Invalid numeric values (flagged, not removed)

| Flag | Rule | Sold | Listing |
|---|---|---|---|
| `invalid_close_price_flag` | ClosePrice <= 0 | 1 | 0 |
| `invalid_living_area_flag` | LivingArea <= 0 | 150 | 360 |
| `invalid_dom_flag` | DaysOnMarket < 0 | 47 | 27 |
| `invalid_bedrooms_flag` | Bedrooms < 0 | 0 | 0 |
| `invalid_bathrooms_flag` | Bathrooms < 0 | 0 | 0 |
| `invalid_numeric_flag` | Any of the above | 198 | 387 |

## 7. Date consistency flags

Expected order: ListingContractDate, then PurchaseContractDate, then CloseDate.

| Flag | Sold | Listing |
|---|---|---|
| `listing_after_close_flag` | 61 | 73 |
| `purchase_after_close_flag` | 240 | 262 |
| `negative_timeline_flag` | 268 | 269 |

## 8. Geographic data quality

Implausible coordinates are those outside a California bounding box (latitude 32.0 to 42.5, longitude -125.0 to -113.5).

| Flag | Sold | Listing |
|---|---|---|
| `missing_coordinates_flag` (lat or lon null) | 15,948 (3.85%) | 80,247 (14.67%) |
| `zero_coordinates_flag` (lat or lon = 0) | 27 (0.01%) | 64 (0.01%) |
| `longitude_positive_flag` (lon > 0) | 31 (0.01%) | 73 (0.01%) |
| `implausible_coordinates_flag` (outside CA box) | 61 (0.01%) | 219 (0.04%) |
| **Rows with at least one geographic issue** | **16,036 (3.87%)** | **80,530 (14.72%)** |

The per-flag counts add up to slightly more than the total because some rows trigger more than one flag (for example, a positive longitude is also outside the California box). Nearly all the geographic problems are simply missing coordinates. The Listing dataset has a higher rate because it includes active listings that were not geocoded.

## 9. Duplicate ListingKey check (flagged, not removed)

| Dataset | Rows flagged | Distinct keys repeated |
|---|---|---|
| Sold | 680 | 338 |
| Listing | 276 | 137 |

`ListingKey` should be unique. The flag marks every row involved so duplicates can be reviewed and are not silently counted twice in later joins or summaries. They are about 0.16% of Sold rows and 0.05% of Listing rows.

## 10. Output files

| File | Rows | Purpose |
|---|---|---|
| `CRMLSSold_Residential_Cleaned.csv` | 414,063 | Analysis-ready Sold dataset with flag columns |
| `CRMLSListing_Residential_Cleaned.csv` | 547,162 | Analysis-ready Listing dataset with flag columns |