============================ LISTING ============================
  Listing: loaded Week1 Output/CRMLSListing_Residential_Combined.csv -> 547162 rows, 84 columns
  [WARNING] Listing: 'BuyerOfficeName' and 'BuyerOfficeName.1' differ in 397276 rows; keeping both for manual review.
  [WARNING] Listing: 'UnparsedAddress' and 'UnparsedAddress.1' differ in 783 rows; keeping both for manual review.
  Listing: found 11 duplicate-header columns in source file, resolved by de-duplication above.

--- [Listing] Dataset Understanding ---
Rows: 547162, Columns: 75
Length: 75, dtype: object
Market analysis fields (24): ['OriginalListPrice', 'CloseDate', 'ClosePrice', 'PropertyType', 'LivingArea', 'ListPrice', 'DaysOnMarket', 'AboveGradeFinishedArea', 'CountyOrParish', 'LotSizeAcres', 'YearBuilt', 'BathroomsTotalInteger', 'City', 'BuildingAreaTotal', 'BedroomsTotal', 'ContractStatusChangeDate', 'PurchaseContractDate', 'ListingContractDate', 'BelowGradeFinishedArea', 'LotSizeDimensions', 'LotSizeArea', 'MainLevelBedrooms', 'PostalCode', 'LotSizeSquareFeet']
Metadata fields (51): ['ListingKey', 'ListAgentEmail', 'ListAgentFirstName', 'ListAgentLastName', 'Latitude', 'Longitude', 'UnparsedAddress', 'ListOfficeName', 'BuyerOfficeName', 'CoListOfficeName', 'ListAgentFullName', 'CoListAgentFirstName', 'CoListAgentLastName', 'BuyerAgentMlsId', 'BuyerAgentFirstName', 'BuyerAgentLastName', 'FireplacesTotal', 'AssociationFeeFrequency', 'ListingKeyNumeric', 'MLSAreaMajor', 'TaxAnnualAmount', 'MlsStatus', 'ElementarySchool', 'AttachedGarageYN', 'ParkingTotal', 'BuilderName', 'PropertySubType', 'SubdivisionName', 'BuyerOfficeAOR', 'BuyerAgencyCompensationType', 'StreetNumberNumeric', 'ListingId', 'BuyerAgencyCompensation', 'TaxYear', 'ElementarySchoolDistrict', 'CoBuyerAgentFirstName', 'BusinessType', 'StateOrProvince', 'CoveredSpaces', 'MiddleOrJuniorSchool', 'FireplaceYN', 'Stories', 'HighSchool', 'Levels', 'NewConstructionYN', 'GarageSpaces', 'HighSchoolDistrict', 'BuyerOfficeName.1', 'AssociationFee', 'MiddleOrJuniorSchoolDistrict', 'UnparsedAddress.1']

--- [Listing] Missing Value Analysis ---
Columns >90% missing (13):
                      column  null_pct
             TaxAnnualAmount    100.00
                BusinessType    100.00
    ElementarySchoolDistrict    100.00
      AboveGradeFinishedArea    100.00
             FireplacesTotal    100.00
MiddleOrJuniorSchoolDistrict    100.00
               CoveredSpaces    100.00
                     TaxYear    100.00
      BelowGradeFinishedArea     99.44
       CoBuyerAgentFirstName     97.50
                 BuilderName     95.36
           LotSizeDimensions     94.79
           BuildingAreaTotal     91.16
Saved missing value report -> Week2 Output/Listing_missing_value_report.csv
Dropping 13 columns: ['TaxAnnualAmount', 'BusinessType', 'ElementarySchoolDistrict', 'AboveGradeFinishedArea', 'FireplacesTotal', 'MiddleOrJuniorSchoolDistrict', 'CoveredSpaces', 'TaxYear', 'BelowGradeFinishedArea', 'CoBuyerAgentFirstName', 'BuilderName', 'LotSizeDimensions', 'BuildingAreaTotal']

--- [Listing] Property Type Filtering ---
Unique PropertyType values found (with counts):
PropertyType
Residential    547162
Rows BEFORE Residential filter: 547162
Rows AFTER Residential filter:  547162
Residential share of dataset: 100.0%

--- [Listing] Null-count summary table (post-filter) ---
ElementarySchool               481686
MiddleOrJuniorSchool           481661
BuyerAgencyCompensation        468169
BuyerAgencyCompensationType    468149
HighSchool                     461270
CoListAgentFirstName           425295
CoListAgentLastName            424892
CoListOfficeName               424799
ClosePrice                     409481
BuyerOfficeAOR                 406788
BuyerOfficeName.1              397275
BuyerOfficeName                397275
BuyerAgentFirstName            395832
BuyerAgentMlsId                395246
BuyerAgentLastName             395138
CloseDate                      388096
SubdivisionName                345955
AssociationFeeFrequency        313802
PurchaseContractDate           285676
MainLevelBedrooms              250485
HighSchoolDistrict             164369
AssociationFee                 132423
Stories                         96473
AttachedGarageYN                95449
Longitude                       80247
Latitude                        80247
MLSAreaMajor                    74488
Levels                          60001
LotSizeAcres                    45030
LotSizeSquareFeet               44350
LotSizeArea                     44176
NewConstructionYN               37596
GarageSpaces                    30245
ContractStatusChangeDate         6311
ListAgentFirstName               4354
ListAgentEmail                   1506
PropertySubType                  1263
StreetNumberNumeric               970
YearBuilt                         927
OriginalListPrice                 789
UnparsedAddress.1                 783
UnparsedAddress                   782
City                              577
FireplaceYN                       572
LivingArea                        552
BedroomsTotal                     133
ListAgentFullName                  92
BathroomsTotalInteger              55
StateOrProvince                    54
ListAgentLastName                  42
ParkingTotal                       20
PostalCode                         13
ListPrice                           0
PropertyType                        0
ListingId                           0
DaysOnMarket                        0
ListOfficeName                      0
ListingKey                          0
CountyOrParish                      0
MlsStatus                           0
ListingContractDate                 0
ListingKeyNumeric                   0

--- [Listing] Numeric Distribution Review ---
  ClosePrice: 9944 extreme outliers flagged (1.5xIQR rule, bounds ~[-525000.00, 2475000.00])


  ListPrice: 45935 extreme outliers flagged (1.5xIQR rule, bounds ~[-619993.75, 2587996.25])


  OriginalListPrice: 45037 extreme outliers flagged (1.5xIQR rule, bounds ~[-630000.00, 2610000.00])


  LivingArea: 27011 extreme outliers flagged (1.5xIQR rule, bounds ~[-330.00, 3878.00])

  LotSizeAcres: 80487 extreme outliers flagged (1.5xIQR rule, bounds ~[-0.17, 0.60])

  BedroomsTotal: 1751 extreme outliers flagged (1.5xIQR rule, bounds ~[-1.00, 7.00])

  BathroomsTotalInteger: 34529 extreme outliers flagged (1.5xIQR rule, bounds ~[0.50, 4.50])

  DaysOnMarket: 48732 extreme outliers flagged (1.5xIQR rule, bounds ~[-19.00, 45.00])

  
  YearBuilt: 1382 extreme outliers flagged (1.5xIQR rule, bounds ~[1901.00, 2061.00])

Saved full numeric distribution summary -> Week2 Output/Listing_numeric_distribution_summary.csv

Required numeric summary (ClosePrice, LivingArea, DaysOnMarket):
       field  count   min       p1      p25   median         mean       p75       p95       p99         max          std
  ClosePrice 137681 525.0 213500.0 600000.0 850000.0 1.203602e+06 1350000.0 2900000.0 5550000.0 820000000.0 4.408814e+06
  LivingArea 546610   0.0    589.0   1248.0   1670.0 1.979898e+03    2300.0    3864.0    6282.0  17021321.0 2.323322e+04
DaysOnMarket 547162 -58.0      0.0      5.0     10.0 1.863006e+01      21.0      71.0     138.0       731.0 2.651861e+01

--- [Listing] Suggested Intern Questions ---
Q1: Residential vs. other PropertyType share (%):
PropertyType
Residential    100.0
Q2: Median ClosePrice: 850,000.00 | Average ClosePrice: 1,203,601.57
Q3: DaysOnMarket distribution (min/25/50/75/max):
count    547162.000000
mean         18.630060
std          26.518612
min         -58.000000
25%           5.000000
50%          10.000000
75%          21.000000
max         731.000000
Q4: Sold above list: 43.42% | below list: 37.84% | at list: 18.73%
Q5: Rows where CloseDate is before ListingContractDate (data issue): 73 (out of 159066 rows with both dates populated)
Q6: Top 10 counties by median ClosePrice:
CountyOrParish
San Mateo        1750000.0
Santa Clara      1649500.0
Marin            1337000.0
San Francisco    1230000.0
Santa Cruz       1215000.0
Alameda          1179000.0
Orange           1170000.0
Monterey          925000.0
Los Angeles       915000.0
San Diego         899000.0


============================ SOLD ============================
  Sold: loaded Week1 Output/CRMLSSold_Residential_Combined.csv -> 414063 rows, 84 columns

--- [Sold] Dataset Understanding ---
Rows: 414063, Columns: 84
Length: 84, dtype: object
Market analysis fields (24): ['OriginalListPrice', 'CloseDate', 'ClosePrice', 'PropertyType', 'LivingArea', 'ListPrice', 'DaysOnMarket', 'AboveGradeFinishedArea', 'CountyOrParish', 'LotSizeAcres', 'YearBuilt', 'BathroomsTotalInteger', 'City', 'BuildingAreaTotal', 'BedroomsTotal', 'ContractStatusChangeDate', 'PurchaseContractDate', 'ListingContractDate', 'BelowGradeFinishedArea', 'LotSizeDimensions', 'LotSizeArea', 'MainLevelBedrooms', 'PostalCode', 'LotSizeSquareFeet']
Metadata fields (60): ['BuyerAgentAOR', 'ListAgentAOR', 'Flooring', 'ViewYN', 'WaterfrontYN', 'BasementYN', 'PoolPrivateYN', 'ListingKey', 'ListAgentEmail', 'ListAgentFirstName', 'ListAgentLastName', 'Latitude', 'Longitude', 'UnparsedAddress', 'ListOfficeName', 'BuyerOfficeName', 'CoListOfficeName', 'ListAgentFullName', 'CoListAgentFirstName', 'CoListAgentLastName', 'BuyerAgentMlsId', 'BuyerAgentFirstName', 'BuyerAgentLastName', 'FireplacesTotal', 'AssociationFeeFrequency', 'ListingKeyNumeric', 'MLSAreaMajor', 'TaxAnnualAmount', 'MlsStatus', 'ElementarySchool', 'AttachedGarageYN', 'ParkingTotal', 'BuilderName', 'PropertySubType', 'SubdivisionName', 'BuyerOfficeAOR', 'StreetNumberNumeric', 'ListingId', 'TaxYear', 'ElementarySchoolDistrict', 'CoBuyerAgentFirstName', 'BusinessType', 'StateOrProvince', 'CoveredSpaces', 'MiddleOrJuniorSchool', 'FireplaceYN', 'Stories', 'HighSchool', 'Levels', 'NewConstructionYN', 'GarageSpaces', 'HighSchoolDistrict', 'AssociationFee', 'MiddleOrJuniorSchoolDistrict', 'OriginatingSystemName', 'OriginatingSystemSubName', 'BuyerAgencyCompensationType', 'BuyerAgencyCompensation', 'latfilled', 'lonfilled']

--- [Sold] Missing Value Analysis ---
Columns >90% missing (15):
                      column  null_pct
               CoveredSpaces    100.00
MiddleOrJuniorSchoolDistrict    100.00
      AboveGradeFinishedArea    100.00
             FireplacesTotal    100.00
                     TaxYear    100.00
    ElementarySchoolDistrict    100.00
                BusinessType    100.00
             TaxAnnualAmount    100.00
                WaterfrontYN     99.94
      BelowGradeFinishedArea     99.42
                  BasementYN     98.04
           LotSizeDimensions     95.14
                 BuilderName     95.11
           BuildingAreaTotal     93.00
       CoBuyerAgentFirstName     90.91
Dropping 15 columns: ['CoveredSpaces', 'MiddleOrJuniorSchoolDistrict', 'AboveGradeFinishedArea', 'FireplacesTotal', 'TaxYear', 'ElementarySchoolDistrict', 'BusinessType', 'TaxAnnualAmount', 'WaterfrontYN', 'BelowGradeFinishedArea', 'BasementYN', 'LotSizeDimensions', 'BuilderName', 'BuildingAreaTotal', 'CoBuyerAgentFirstName']

--- [Sold] Property Type Filtering ---
Unique PropertyType values found (with counts):
PropertyType
Residential    414063
Rows BEFORE Residential filter: 414063
Rows AFTER Residential filter:  414063
Residential share of dataset: 100.0%

--- [Sold] Null-count summary table (post-filter) ---
BuyerAgencyCompensation        367938
BuyerAgencyCompensationType    367927
ElementarySchool               358949
MiddleOrJuniorSchool           358559
OriginatingSystemSubName       358351
OriginatingSystemName          358351
lonfilled                      350179
latfilled                      350179
HighSchool                     341999
CoListAgentFirstName           319167
CoListAgentLastName            318921
CoListOfficeName               316067
SubdivisionName                260044
AssociationFeeFrequency        241544
MainLevelBedrooms              173800
Flooring                       148592
HighSchoolDistrict             113643
AssociationFee                  94701
Stories                         63800
AttachedGarageYN                63267
MLSAreaMajor                    55359
BuyerAgentAOR                   50882
ListAgentAOR                    46189
Levels                          39924
PoolPrivateYN                   35669
ViewYN                          35261
LotSizeAcres                    32539
LotSizeSquareFeet               32137
LotSizeArea                     32008
NewConstructionYN               30731
BuyerOfficeAOR                  23324
GarageSpaces                    17760
Latitude                        15948
Longitude                       15948
BuyerOfficeName                  6743
ListAgentFirstName               3108
BuyerAgentFirstName              2010
ListAgentEmail                   1061
PropertySubType                   804
OriginalListPrice                 757
ContractStatusChangeDate          589
BuyerAgentMlsId                   534
StreetNumberNumeric               479
ParkingTotal                      426
UnparsedAddress                   391
YearBuilt                         372
FireplaceYN                       331
City                              311
LivingArea                        234
PurchaseContractDate              195
BuyerAgentLastName                175
ListAgentFullName                  92
BathroomsTotalInteger              69
ListAgentLastName                  40
BedroomsTotal                      11
ClosePrice                          2
PostalCode                          2
ListingContractDate                 1
MlsStatus                           0
DaysOnMarket                        0
PropertyType                        0
ListingKey                          0
ListingId                           0
ListPrice                           0
CloseDate                           0
StateOrProvince                     0
ListOfficeName                      0
CountyOrParish                      0
ListingKeyNumeric                   0

--- [Sold] Numeric Distribution Review ---
  ClosePrice: 30776 extreme outliers flagged (1.5xIQR rule, bounds ~[-512500.00, 2387500.00])

  ListPrice: 31056 extreme outliers flagged (1.5xIQR rule, bounds ~[-502015.00, 2373209.00])

  OriginalListPrice: 32258 extreme outliers flagged (1.5xIQR rule, bounds ~[-486000.00, 2370000.00])

  LivingArea: 18210 extreme outliers flagged (1.5xIQR rule, bounds ~[-208.50, 3675.50])

  LotSizeAcres: 59352 extreme outliers flagged (1.5xIQR rule, bounds ~[-0.11, 0.50])

  BedroomsTotal: 22737 extreme outliers flagged (1.5xIQR rule, bounds ~[1.50, 5.50])

  BathroomsTotalInteger: 19048 extreme outliers flagged (1.5xIQR rule, bounds ~[0.50, 4.50])

  DaysOnMarket: 31801 extreme outliers flagged (1.5xIQR rule, bounds ~[-52.00, 108.00])

  YearBuilt: 977 extreme outliers flagged (1.5xIQR rule, bounds ~[1901.50, 2057.50])


Required numeric summary (ClosePrice, LivingArea, DaysOnMarket):
       field  count    min       p1      p25   median         mean       p75       p95       p99         max          std
  ClosePrice 414061    0.0 202320.0 575000.0 823000.0 1.193871e+06 1300000.0 2850000.0 5575000.0 989500000.0 6.290055e+06
  LivingArea 413829    0.0    604.0   1248.0   1642.0 1.903808e+03    2219.0    3560.0    5282.0  17021321.0 2.647591e+04
DaysOnMarket 414063 -288.0      0.0      8.0     18.0 3.735501e+01      48.0     132.0     231.0     12430.0 5.359260e+01

--- [Sold] Suggested Intern Questions ---
Q1: Residential vs. other PropertyType share (%):
PropertyType
Residential    100.0
Q2: Median ClosePrice: 823,000.00 | Average ClosePrice: 1,193,871.09
Q3: DaysOnMarket distribution (min/25/50/75/max):
count    414063.000000
mean         37.355014
std          53.592602
min        -288.000000
25%           8.000000
50%          18.000000
75%          48.000000
max       12430.000000
Q4: Sold above list: 40.10% | below list: 42.55% | at list: 17.35%
Q5: Rows where CloseDate is before ListingContractDate (data issue): 61 (out of 414062 rows with both dates populated)
Q6: Top 10 counties by median ClosePrice:
CountyOrParish
Del Norte        2485000.0
Other County     2462500.0
San Mateo        1700000.0
Santa Clara      1600000.0
Santa Cruz       1200000.0
San Francisco    1198950.0
Orange           1175000.0
Marin            1165000.0
Alameda          1133000.0
Alpine           1100000.0

Saved Residential-filtered dataset -> Week2 Output/CRMLSSold_Residential_Filtered.csv