# Week 7 Summary: Outlier Detection and Data Quality

## 1. Approach

flag outliers rather than delete records

previously flagged: 
`invalid_close_price_flag`, `invalid_living_area_flag` and `invalid_dom_flag` mark records that are invalid outright (for example ClosePrice <= 0).

Flagged Outliers:  For each of ClosePrice, LivingArea, DaysOnMarket, `price_per_sqft` and `close_to_original_list_ratio`, a record is flagged if it falls outside [Q1 - 1.5 x IQR, Q3 + 1.5 x IQR]. Q1 and Q3 are computed only on Tier-1-valid, non-null rows, so invalid values such as a $0 price cannot distort the bounds.

- **Two outputs per dataset.** A full flagged file (every row, all flag columns, nothing removed) and a filtered analysis file (`any_outlier_flag == False`).

| Dataset | Input rows | Columns in |
|---|---|---|
| Sold | 414,063 | 81 |
| Listing | 547,162 | 76 |

## 2. IQR bounds and flags per field

### Sold

| Field | Q1 | Q3 | Lower bound | Upper bound | Rows flagged | % of all rows |
|---|---|---|---|---|---|---|
| ClosePrice | 575,000 | 1,300,000 | -512,500 | 2,387,500 | 30,776 | 7.43% |
| LivingArea | 1,248 | 2,219 | -208.5 | 3,675.5 | 18,210 | 4.40% |
| DaysOnMarket | 8 | 48 | -52 | 108 | 31,793 | 7.68% |
| price_per_sqft | 368.39 | 732.37 | -177.60 | 1,278.35 | 17,452 | 4.21% |
| close_to_original_list_ratio | 0.95 | 1.02 | 0.85 | 1.12 | 39,162 | 9.46% |

### Listing

| Field | Q1 | Q3 | Lower bound | Upper bound | Rows flagged | % of all rows |
|---|---|---|---|---|---|---|
| ClosePrice | 600,000 | 1,350,000 | -525,000 | 2,475,000 | 9,944 | 1.82% |
| LivingArea | 1,248 | 2,300 | -330 | 3,878 | 27,011 | 4.94% |
| DaysOnMarket | 5 | 21 | -19 | 45 | 48,728 | 8.91% |
| price_per_sqft | 393.84 | 762.09 | -158.55 | 1,314.47 | 6,266 | 1.15% |
| close_to_original_list_ratio | 0.97 | 1.03 | 0.88 | 1.12 | 14,005 | 2.56% |

Percentiles printed alongside the bounds for context (Sold ClosePrice: p1 = $202K, p5 = $340K, p95 = $2.85M, p99 = $5.58M) show a long right tail, which is what the upper bound is trimming.

## 3. Combined flags

| Dataset | Rows flagged by at least one rule | Share |
|---|---|---|
| Sold | 95,456 | 23.05% |
| Listing | 89,703 | 16.39% |

A row is counted once even if it is flagged on several fields, which is why these totals are smaller than the sum of the per-field counts above.

## 4. Before / after comparison

### Dataset size

| Dataset | Before | After | Excluded | % excluded |
|---|---|---|---|---|
| Sold | 414,063 | 318,607 | 95,456 | 23.05% |
| Listing | 547,162 | 457,459 | 89,703 | 16.39% |

### Median values

| Dataset | Field | Before | After | Change |
|---|---|---|---|---|
| Sold | ClosePrice | $823,000 | $769,000 | -6.56% |
| Sold | LivingArea | 1,642 | 1,579 | -3.84% |
| Sold | DaysOnMarket | 18 | 16 | -11.11% |
| Listing | ClosePrice | $850,000 | $800,000 | -5.88% |
| Listing | LivingArea | 1,670 | 1,617 | -3.17% |
| Listing | DaysOnMarket | 10 | 9 | -10.00% |

## 5. What the comparison shows

- **Medians move down after filtering.** The filtered Sold dataset has a median price about 6.6% lower and a median DOM 2 days shorter. Most flagged rows are on the high side (luxury prices, large homes, slow sales), so removing them pulls every median down.
- **The filtered file is not a drop-in replacement for the full market.** Because the upper price bound is about $2.39M for Sold and $2.48M for Listing, homes above those levels are excluded from the filtered file even though they are real sales. Use the filtered file for "typical market" dashboards and the full flagged file when high-end segments matter.
- **Nothing was permanently deleted.** Every excluded row is still in the `_Flagged.csv` files with the flag columns showing why.

## 6. Output files

| File | Rows | Purpose |
|---|---|---|
| `CRMLSSold_Residential_Flagged.csv` | 414,063 | Full audit dataset with all flag columns |
| `CRMLSSold_Residential_FilteredForAnalysis.csv` | 318,607 | Analysis dataset for Tableau |
| `CRMLSListing_Residential_Flagged.csv` | 547,162 | Full audit dataset with all flag columns |
| `CRMLSListing_Residential_FilteredForAnalysis.csv` | 457,459 | Analysis dataset for Tableau |

## 7. Caveats and notes

- **Percentages for Listing are measured against all rows, including active listings.** Close-based fields (ClosePrice, `price_per_sqft`, `close_to_original_list_ratio`) are only populated for roughly 137K to 159K closed records, so the true flag rate within closed records is higher than shown (roughly 6% for ClosePrice, 4.6% for `price_per_sqft`, and 10% for the ratio). Active listings have null values there, so they are never flagged and remain in the filtered file.
- **The IQR lower bounds are negative for price, area and DOM.** The method therefore only flags the high end for those fields. Low-end oddities, such as a $10,000 sale, are only caught if Tier 1 rules already mark them. Percentiles (p1 = $202K for Sold ClosePrice) or a log transform could be used if low-end screening is wanted.
- **DOM and the price ratio are flagged heavily (7.7% to 9.5% in Sold) because they are skewed.** A property that sat 120 days or closed at 85% of its original list price is unusual but real, so these flags mark "unusual", not "wrong". Reading `any_outlier_flag` as "invalid" would overstate the problem.