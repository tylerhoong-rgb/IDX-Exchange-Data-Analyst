============================ SOLD ============================
  Loaded Week3 Output/CRMLSSold_Residential_WithRates.csv: 414063 rows, 71 columns

--- [Sold] Date Field Conversion ---
  CloseDate: str -> datetime64[us] (0 null/unparseable after conversion)
  PurchaseContractDate: str -> datetime64[us] (195 null/unparseable after conversion)
  ListingContractDate: str -> datetime64[us] (1 null/unparseable after conversion)
  ContractStatusChangeDate: str -> datetime64[us] (589 null/unparseable after conversion)

--- [Sold] Redundant Column Removal ---
  Columns before: 71
  Dropping 'ListAgentEmail' -- agent contact info, not needed for market analytics
  Dropping 'BuyerAgentMlsId' -- agent identifier, not needed for market analytics
  Dropping 'BuyerAgentFirstName' -- agent contact info
  Dropping 'BuyerAgentLastName' -- agent contact info
  Dropping 'CoListOfficeName' -- office info, not needed for market analytics
  Dropping 'BuyerOfficeAOR' -- office board code, not needed for market analytics
  Dropping 'BuyerAgentAOR' -- agent board code, not needed for market analytics
  Dropping 'ListAgentAOR' -- agent board code, not needed for market analytics
  Dropping 'BuyerAgencyCompensationType' -- commission info, not needed for market analytics
  Dropping 'BuyerAgencyCompensation' -- commission info, not needed for market analytics
  Dropping 'ListingKeyNumeric' -- duplicate of ListingKey in numeric form
  Dropping 'StreetNumberNumeric' -- redundant, derivable from UnparsedAddress
  Dropping 'OriginatingSystemName' -- constant source-system metadata, not analytical
  Dropping 'OriginatingSystemSubName' -- constant source-system metadata, not analytical
  Columns after: 57

--- [Sold] Missing Value Handling ---
  45 columns contain at least one null value

--- [Sold] Invalid Numeric Value Flags ---
  invalid_close_price_flag: 1 rows flagged
  invalid_living_area_flag: 150 rows flagged
  invalid_dom_flag: 47 rows flagged
  invalid_bedrooms_flag: 0 rows flagged
  invalid_bathrooms_flag: 0 rows flagged
  invalid_numeric_flag: 198 rows flagged

--- [Sold] Date Consistency Flags ---
  listing_after_close_flag: 61 rows flagged
  purchase_after_close_flag: 240 rows flagged
  negative_timeline_flag: 268 rows flagged

--- [Sold] Geographic Data Quality ---
  missing_coordinates_flag: 15948 rows flagged (3.85%)
  zero_coordinates_flag: 27 rows flagged (0.01%)
  longitude_positive_flag: 31 rows flagged (0.01%)
  implausible_coordinates_flag: 61 rows flagged (0.01%)
  TOTAL rows with at least one geographic data quality issue: 16036 (3.87%)

--- [Sold] Duplicate ListingKey Check ---
  duplicate_listing_key_flag: 680 rows flagged (338 distinct ListingKey values appear more than once)

--- [Sold] Final dtype confirmation (date & numeric fields) ---
  CloseDate: datetime64[us]
  PurchaseContractDate: datetime64[us]
  ListingContractDate: datetime64[us]
  ContractStatusChangeDate: datetime64[us]
  ClosePrice: float64
  ListPrice: float64
  OriginalListPrice: float64
  LivingArea: float64
  LotSizeAcres: float64
  LotSizeArea: float64
  LotSizeSquareFeet: float64
  BedroomsTotal: float64
  BathroomsTotalInteger: float64
  DaysOnMarket: int64
  YearBuilt: float64
  Latitude: float64
  Longitude: float64
  AssociationFee: float64
  ParkingTotal: float64
  GarageSpaces: float64
  Stories: float64
  MainLevelBedrooms: float64

============================ LISTING ============================
  Loaded Week3 Output/CRMLSListing_Residential_WithRates.csv: 547162 rows, 64 columns

--- [Listing] Date Field Conversion ---
  CloseDate: str -> datetime64[us] (388096 null/unparseable after conversion)
  PurchaseContractDate: str -> datetime64[us] (285676 null/unparseable after conversion)
  ListingContractDate: str -> datetime64[us] (0 null/unparseable after conversion)
  ContractStatusChangeDate: str -> datetime64[us] (6311 null/unparseable after conversion)

--- [Listing] Redundant Column Removal ---
  Columns before: 64
  Dropping 'ListAgentEmail' -- agent contact info, not needed for market analytics
  Dropping 'BuyerAgentMlsId' -- agent identifier, not needed for market analytics
  Dropping 'BuyerAgentFirstName' -- agent contact info
  Dropping 'BuyerAgentLastName' -- agent contact info
  Dropping 'BuyerOfficeName.1' -- duplicate of BuyerOfficeName (raw export had duplicate header)
  Dropping 'CoListOfficeName' -- office info, not needed for market analytics
  Dropping 'BuyerOfficeAOR' -- office board code, not needed for market analytics
  Dropping 'BuyerAgencyCompensationType' -- commission info, not needed for market analytics
  Dropping 'BuyerAgencyCompensation' -- commission info, not needed for market analytics
  Dropping 'ListingKeyNumeric' -- duplicate of ListingKey in numeric form
  Dropping 'StreetNumberNumeric' -- redundant, derivable from UnparsedAddress
  Dropping 'UnparsedAddress.1' -- duplicate of UnparsedAddress (raw export had duplicate header)
  Columns after: 52

--- [Listing] Missing Value Handling ---
  41 columns contain at least one null value

--- [Listing] Invalid Numeric Value Flags ---
  invalid_close_price_flag: 0 rows flagged
  invalid_living_area_flag: 360 rows flagged
  invalid_dom_flag: 27 rows flagged
  invalid_bedrooms_flag: 0 rows flagged
  invalid_bathrooms_flag: 0 rows flagged
  invalid_numeric_flag: 387 rows flagged

--- [Listing] Date Consistency Flags ---
  listing_after_close_flag: 73 rows flagged
  purchase_after_close_flag: 262 rows flagged
  negative_timeline_flag: 269 rows flagged

--- [Listing] Geographic Data Quality ---
  missing_coordinates_flag: 80247 rows flagged (14.67%)
  zero_coordinates_flag: 64 rows flagged (0.01%)
  longitude_positive_flag: 73 rows flagged (0.01%)
  implausible_coordinates_flag: 219 rows flagged (0.04%)
  TOTAL rows with at least one geographic data quality issue: 80530 (14.72%)

--- [Listing] Duplicate ListingKey Check ---
  duplicate_listing_key_flag: 276 rows flagged (137 distinct ListingKey values appear more than once)

--- [Listing] Final dtype confirmation (date & numeric fields) ---
  CloseDate: datetime64[us]
  PurchaseContractDate: datetime64[us]
  ListingContractDate: datetime64[us]
  ContractStatusChangeDate: datetime64[us]
  ClosePrice: float64
  ListPrice: float64
  OriginalListPrice: float64
  LivingArea: float64
  LotSizeAcres: float64
  LotSizeArea: float64
  LotSizeSquareFeet: float64
  BedroomsTotal: float64
  BathroomsTotalInteger: float64
  DaysOnMarket: int64
  YearBuilt: float64
  Latitude: float64
  Longitude: float64
  AssociationFee: float64
  ParkingTotal: float64
  GarageSpaces: float64
  Stories: float64
  MainLevelBedrooms: float64


quick summary:
conversion to datetime format: clarification on null/unparsable null values already existed, conversion did not create new null values
Redundant Column Removal: 14 for sold, 12 for listing
missing values: 45 cols for sold, 41 cols for listing
invalid numeric values: some flagged for both sold and listing
data consistency: some flagged for both sold and listing

--- [Sold] Geographic Data Quality ---
  missing_coordinates_flag: 15948 rows flagged (3.85%)
  zero_coordinates_flag: 27 rows flagged (0.01%)
  longitude_positive_flag: 31 rows flagged (0.01%)
  implausible_coordinates_flag: 61 rows flagged (0.01%)
  TOTAL rows with at least one geographic data quality issue: 16036 (3.87%)

  --- [Listing] Geographic Data Quality ---
  missing_coordinates_flag: 80247 rows flagged (14.67%)
  zero_coordinates_flag: 64 rows flagged (0.01%)
  longitude_positive_flag: 73 rows flagged (0.01%)
  implausible_coordinates_flag: 219 rows flagged (0.04%)
  TOTAL rows with at least one geographic data quality issue: 80530 (14.72%)

  
