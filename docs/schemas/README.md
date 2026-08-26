# CBO Baseline Dataset Schemas

One schema document exists for every processed CSV in `data/processed/`. Each file documents column definitions, provenance, and aggregation caveats.

**Total datasets:** 230

## Column reference (all datasets share this schema)

| Column | Type | Description | Unit | Example | Notes |
|---|---|---|---|---|---|
| `program` | string | Canonical CBO program name keyed by the stable source identifier. | N/A | — | Stable across workbook vintages; use ``program_id`` as the machine key. |
| `category` | string | Leaf line-item label from the source worksheet. | N/A | — | Rows where ``is_total`` is ``true`` represent aggregated totals or subtotals and should be excluded from sum-based aggregations to avoid double-counting. |
| `fiscal_year` | integer or null | Annual federal fiscal year; blank for every other period type. | Year | — | Historical actuals are retained. Consult ``period_type`` and the explicit period bounds before interpreting a row as annual fiscal-year data. |
| `value` | float | Parsed numeric value from the source cell. | See ``unit`` column | — | Negative values indicate outflows or reductions. Values originally enclosed in parentheses (e.g. ``(123)``) are converted to negative floats. |
| `unit` | string | Unit of measure for ``value``, resolved from row/section labels and parse metadata. | N/A | — | Common values include 'Millions of dollars', 'Billions of dollars', and 'Thousands'. |
| `source_file` | string | Original CBO workbook filename from ``data/raw/``. | N/A | — | Use this column to trace any row back to its exact source workbook. |
| `source_sheet` | string | Worksheet name within the source workbook. | N/A | — | Combine with source file, row, and column for exact cell provenance. |
| `is_total` | boolean | ``true`` if the category label contains the word 'total' or 'subtotal', indicating an aggregated row. | N/A | — | **Always filter ``is_total = true`` rows out before computing sums or averages** across categories to avoid double-counting. Retain them for headline/summary views. |
| `program_id` | string | Stable numeric CBO identifier from the source filename. | N/A | — | Preferred program join key across vintages. |
| `category_path` | string | Hierarchy-aware path from table/section headings to the leaf category. | N/A | — | Use this field instead of ``category`` when labels repeat in different subprograms. |
| `period_type` | string | Period semantics for the observation. | N/A | — | Values include fiscal_year, calendar_year, award_year, school_year, cumulative_fiscal_years, and unmapped. |
| `period_start_year` | integer or null | First year represented by the source period. | Year | — | Equals period_end_year for annual rows and is blank when the source period is not identified. |
| `period_end_year` | integer or null | Last year represented by the source period. | Year | — | For annual fiscal-year rows this equals ``fiscal_year``. |
| `period_label` | string | Normalized source period label such as 2025 or 2025-2029. | N/A | — | Rows with unrecognized periods are labeled explicitly rather than assigned a guessed year. |
| `source_row` | integer | One-based worksheet row containing the numeric source value. | N/A | — | Together with ``source_column`` identifies the exact source cell. |
| `source_column` | integer | One-based worksheet column containing the numeric source value. | N/A | — | Together with ``source_row`` identifies the exact source cell. |

## Dataset index

| Dataset | Rows | Fiscal years | Programs | Schema |
|---|---|---|---|---|
| `aatf_0_2023_05` | 231 | 2023–2033 | Airport and Airway Trust Fund | [aatf_0_2023_05.md](aatf_0_2023_05.md) |
| `aatf_2024_02` | 231 | 2024–2034 | Airport and Airway Trust Fund | [aatf_2024_02.md](aatf_2024_02.md) |
| `aatf_2024_06` | 231 | 2024–2034 | Airport and Airway Trust Fund | [aatf_2024_06.md](aatf_2024_06.md) |
| `aatf_2025_01` | 209 | 2025–2035 | Airport and Airway Trust Fund | [aatf_2025_01.md](aatf_2025_01.md) |
| `aatf_2026_02` | 209 | 2026–2036 | Airport and Airway Trust Fund | [aatf_2026_02.md](aatf_2026_02.md) |
| `child_nutrition_2019_05` | 249 | 2012–2029 | Child Nutrition | [child_nutrition_2019_05.md](child_nutrition_2019_05.md) |
| `child_support_enforcement_2019_05` | 55 | 2019–2029 | Child Support Enforcement | [child_support_enforcement_2019_05.md](child_support_enforcement_2019_05.md) |
| `childnutrition_0_2022_05` | 186 | 2022–2032 | Child Nutrition | [childnutrition_0_2022_05.md](childnutrition_0_2022_05.md) |
| `childnutrition_0_2024_02` | 218 | 2024–2034 | Child Nutrition | [childnutrition_0_2024_02.md](childnutrition_0_2024_02.md) |
| `childnutrition_2020_01` | 121 | 2020–2030 | Child Nutrition | [childnutrition_2020_01.md](childnutrition_2020_01.md) |
| `childnutrition_2020_03` | 121 | 2020–2030 | Child Nutrition | [childnutrition_2020_03.md](childnutrition_2020_03.md) |
| `childnutrition_2021_02` | 186 | 2021–2031 | Child Nutrition | [childnutrition_2021_02.md](childnutrition_2021_02.md) |
| `childnutrition_2021_07` | 186 | 2021–2031 | Child Nutrition | [childnutrition_2021_07.md](childnutrition_2021_07.md) |
| `childnutrition_2023_05` | 186 | 2023–2033 | Child Nutrition | [childnutrition_2023_05.md](childnutrition_2023_05.md) |
| `childnutrition_2024_06` | 218 | 2024–2034 | Child Nutrition | [childnutrition_2024_06.md](childnutrition_2024_06.md) |
| `childnutrition_2025_01` | 218 | 2025–2035 | Child Nutrition | [childnutrition_2025_01.md](childnutrition_2025_01.md) |
| `childsupportenforcement_2020_01` | 55 | 2020–2030 | Child Support Enforcement | [childsupportenforcement_2020_01.md](childsupportenforcement_2020_01.md) |
| `childsupportenforcement_2020_03` | 55 | 2020–2030 | Child Support Enforcement | [childsupportenforcement_2020_03.md](childsupportenforcement_2020_03.md) |
| `childsupportenforcement_2021_02` | 88 | 2021–2031 | Child Support Enforcement | [childsupportenforcement_2021_02.md](childsupportenforcement_2021_02.md) |
| `childsupportenforcement_2021_07` | 44 | 2021–2031 | Child Support Enforcement | [childsupportenforcement_2021_07.md](childsupportenforcement_2021_07.md) |
| `chip_2019_05` | 151 | 2018–2029 | CHIP | [chip_2019_05.md](chip_2019_05.md) |
| `chip_2020_03` | 138 | 2019–2030 | CHIP | [chip_2020_03.md](chip_2020_03.md) |
| `chip_2021_07` | 99 | 2021–2031 | CHIP | [chip_2021_07.md](chip_2021_07.md) |
| `chip_2022_05` | 108 | 2021–2032 | CHIP | [chip_2022_05.md](chip_2022_05.md) |
| `chip_2023_05` | 108 | 2022–2033 | CHIP | [chip_2023_05.md](chip_2023_05.md) |
| `chip_2024_06` | 99 | 2024–2034 | CHIP | [chip_2024_06.md](chip_2024_06.md) |
| `chip_2026_02` | 55 | 2026–2036 | CHIP | [chip_2026_02.md](chip_2026_02.md) |
| `csec_0_2022_05` | 55 | 2022–2032 | Child Support Enforcement | [csec_0_2022_05.md](csec_0_2022_05.md) |
| `csec_2023_05` | 55 | 2023–2033 | Child Support Enforcement | [csec_2023_05.md](csec_2023_05.md) |
| `csec_2024_02` | 55 | 2024–2034 | Child Support Enforcement | [csec_2024_02.md](csec_2024_02.md) |
| `csec_2024_06` | 54 | 2024–2034 | Child Support Enforcement | [csec_2024_06.md](csec_2024_06.md) |
| `csec_2025_01` | 65 | 2025–2035 | Child Support Enforcement | [csec_2025_01.md](csec_2025_01.md) |
| `customs_fees_2025_01` | 48 | 2025–2035 | Customs Fees | [customs_fees_2025_01.md](customs_fees_2025_01.md) |
| `dodmedicare_2019_05` | 132 | 2019–2029 | DoD Medicare | [dodmedicare_2019_05.md](dodmedicare_2019_05.md) |
| `dodmedicare_2020_01` | 132 | 2020–2030 | DoD Medicare | [dodmedicare_2020_01.md](dodmedicare_2020_01.md) |
| `dodmedicare_2020_03` | 132 | 2020–2030 | DoD Medicare | [dodmedicare_2020_03.md](dodmedicare_2020_03.md) |
| `dodmedicare_2021_02` | 121 | 2021–2031 | DoD Medicare | [dodmedicare_2021_02.md](dodmedicare_2021_02.md) |
| `dodmedicare_2021_07` | 121 | 2021–2031 | DoD Medicare | [dodmedicare_2021_07.md](dodmedicare_2021_07.md) |
| `dodmedicare_2022_05` | 121 | 2022–2032 | DoD Medicare | [dodmedicare_2022_05.md](dodmedicare_2022_05.md) |
| `dodmedicare_2023_05` | 121 | 2023–2033 | DoD Medicare | [dodmedicare_2023_05.md](dodmedicare_2023_05.md) |
| `dodmedicare_2024_02` | 121 | 2024–2034 | DoD Medicare | [dodmedicare_2024_02.md](dodmedicare_2024_02.md) |
| `dodmedicare_2025_01` | 121 | 2025–2035 | DoD Medicare | [dodmedicare_2025_01.md](dodmedicare_2025_01.md) |
| `fdic_2024_06` | 60 | 2023–2034 | FDIC | [fdic_2024_06.md](fdic_2024_06.md) |
| `fdic_2025_01` | 52 | 2023–2035 | FDIC | [fdic_2025_01.md](fdic_2025_01.md) |
| `foster_care_2019_05` | 264 | 2019–2029 | Foster Care | [foster_care_2019_05.md](foster_care_2019_05.md) |
| `fostercare_2020_01` | 275 | 2020–2030 | Foster Care | [fostercare_2020_01.md](fostercare_2020_01.md) |
| `fostercare_2020_03` | 275 | 2020–2030 | Foster Care | [fostercare_2020_03.md](fostercare_2020_03.md) |
| `fostercare_2021_02` | 275 | 2021–2031 | Foster Care | [fostercare_2021_02.md](fostercare_2021_02.md) |
| `fostercare_2021_07` | 275 | 2021–2031 | Foster Care | [fostercare_2021_07.md](fostercare_2021_07.md) |
| `fostercare_2022_05` | 253 | 2022–2032 | Foster Care | [fostercare_2022_05.md](fostercare_2022_05.md) |
| `fostercare_2023_05` | 74 | 2003–2055 | Foster Care | [fostercare_2023_05.md](fostercare_2023_05.md) |
| `fostercare_2024_02` | 253 | 2024–2034 | Foster Care | [fostercare_2024_02.md](fostercare_2024_02.md) |
| `fostercare_2024_06` | 253 | 2024–2034 | Foster Care | [fostercare_2024_06.md](fostercare_2024_06.md) |
| `fostercare_2025_01` | 253 | 2025–2035 | Foster Care | [fostercare_2025_01.md](fostercare_2025_01.md) |
| `fostercare_2026_02` | 253 | 2026–2036 | Foster Care | [fostercare_2026_02.md](fostercare_2026_02.md) |
| `health_insurance_2019_05` | 1,297 | 2018–2029 | Health Insurance | [health_insurance_2019_05.md](health_insurance_2019_05.md) |
| `healthinsurance_2020_03` | 1,156 | 2018–2030 | Health Insurance | [healthinsurance_2020_03.md](healthinsurance_2020_03.md) |
| `healthinsurance_2020_09` | 1,187 | 2018–2030 | Health Insurance | [healthinsurance_2020_09.md](healthinsurance_2020_09.md) |
| `healthinsurance_2021_07` | 473 | 2021–2031 | Health Insurance | [healthinsurance_2021_07.md](healthinsurance_2021_07.md) |
| `healthinsurance_2022_06` | 472 | 2022–2032 | Health Insurance | [healthinsurance_2022_06.md](healthinsurance_2022_06.md) |
| `healthinsurance_2023_05` | 440 | 2023–2033 | Health Insurance | [healthinsurance_2023_05.md](healthinsurance_2023_05.md) |
| `healthinsurance_2023_09` | 473 | 2023–2033 | Health Insurance | [healthinsurance_2023_09.md](healthinsurance_2023_09.md) |
| `healthinsurance_2024_06` | 507 | 2023–2034 | Health Insurance | [healthinsurance_2024_06.md](healthinsurance_2024_06.md) |
| `highway_trust_fund_2019_05` | 106 | 2018–2029 | Highway Trust Fund | [highway_trust_fund_2019_05.md](highway_trust_fund_2019_05.md) |
| `highwaytrustfund_2020_01` | 103 | 2019–2030 | Highway Trust Fund | [highwaytrustfund_2020_01.md](highwaytrustfund_2020_01.md) |
| `highwaytrustfund_2020_03` | 103 | 2019–2030 | Highway Trust Fund | [highwaytrustfund_2020_03.md](highwaytrustfund_2020_03.md) |
| `highwaytrustfund_2021_02` | 126 | 2020–2031 | Highway Trust Fund | [highwaytrustfund_2021_02.md](highwaytrustfund_2021_02.md) |
| `highwaytrustfund_2021_07` | 127 | 2020–2031 | Highway Trust Fund | [highwaytrustfund_2021_07.md](highwaytrustfund_2021_07.md) |
| `highwaytrustfund_2022_05` | 134 | 2021–2032 | Highway Trust Fund | [highwaytrustfund_2022_05.md](highwaytrustfund_2022_05.md) |
| `highwaytrustfund_2023_05` | 134 | 2022–2033 | Highway Trust Fund | [highwaytrustfund_2023_05.md](highwaytrustfund_2023_05.md) |
| `highwaytrustfund_2024_02` | 108 | 2023–2034 | Highway Trust Fund | [highwaytrustfund_2024_02.md](highwaytrustfund_2024_02.md) |
| `highwaytrustfund_2024_06` | 108 | 2023–2034 | Highway Trust Fund | [highwaytrustfund_2024_06.md](highwaytrustfund_2024_06.md) |
| `highwaytrustfund_2025_01` | 116 | 2024–2035 | Highway Trust Fund | [highwaytrustfund_2025_01.md](highwaytrustfund_2025_01.md) |
| `medicaid_2019_05` | 316 | 2018–2029 | Medicaid | [medicaid_2019_05.md](medicaid_2019_05.md) |
| `medicaid_2020_03` | 316 | 2019–2030 | Medicaid | [medicaid_2020_03.md](medicaid_2020_03.md) |
| `medicaid_2021_07` | 336 | 2020–2031 | Medicaid | [medicaid_2021_07.md](medicaid_2021_07.md) |
| `medicaid_2022_05` | 336 | 2021–2032 | Medicaid | [medicaid_2022_05.md](medicaid_2022_05.md) |
| `medicaid_2023_05` | 336 | 2022–2033 | Medicaid | [medicaid_2023_05.md](medicaid_2023_05.md) |
| `medicaid_2024_06` | 308 | 2024–2034 | Medicaid | [medicaid_2024_06.md](medicaid_2024_06.md) |
| `medicaid_2026_02` | 336 | 2025–2036 | Medicaid | [medicaid_2026_02.md](medicaid_2026_02.md) |
| `medicare_2019_05` | 653 | 2018–2029 | Medicare | [medicare_2019_05.md](medicare_2019_05.md) |
| `medicare_2020_03` | 687 | 2019–2030 | Medicare | [medicare_2020_03.md](medicare_2020_03.md) |
| `medicare_2021_07` | 495 | 2020–2031 | Medicare | [medicare_2021_07.md](medicare_2021_07.md) |
| `medicare_2022_05` | 511 | 2021–2032 | Medicare | [medicare_2022_05.md](medicare_2022_05.md) |
| `medicare_2023_05` | 528 | 2022–2033 | Medicare | [medicare_2023_05.md](medicare_2023_05.md) |
| `medicare_2024_06` | 516 | 2023–2034 | Medicare | [medicare_2024_06.md](medicare_2024_06.md) |
| `medicare_2026_02` | 516 | 2025–2036 | Medicare | [medicare_2026_02.md](medicare_2026_02.md) |
| `military_retirement_2019_05` | 99 | 2019–2029 | Military Retirement | [military_retirement_2019_05.md](military_retirement_2019_05.md) |
| `militaryretirement_0_2022_05` | 96 | 2022–2032 | Military Retirement | [militaryretirement_0_2022_05.md](militaryretirement_0_2022_05.md) |
| `militaryretirement_2020_01` | 99 | 2020–2030 | Military Retirement | [militaryretirement_2020_01.md](militaryretirement_2020_01.md) |
| `militaryretirement_2020_03` | 99 | 2020–2030 | Military Retirement | [militaryretirement_2020_03.md](militaryretirement_2020_03.md) |
| `militaryretirement_2021_02` | 88 | 2021–2031 | Military Retirement | [militaryretirement_2021_02.md](militaryretirement_2021_02.md) |
| `militaryretirement_2023_05` | 96 | 2023–2033 | Military Retirement | [militaryretirement_2023_05.md](militaryretirement_2023_05.md) |
| `militaryretirement_2024_06` | 96 | 2024–2034 | Military Retirement | [militaryretirement_2024_06.md](militaryretirement_2024_06.md) |
| `mortgages_0_2022_05` | 153 | 2022–2032 | Mortgages | [mortgages_0_2022_05.md](mortgages_0_2022_05.md) |
| `mortgages_2019_05` | 153 | 2019–2029 | Mortgages | [mortgages_2019_05.md](mortgages_2019_05.md) |
| `mortgages_2020_01` | 153 | 2020–2030 | Mortgages | [mortgages_2020_01.md](mortgages_2020_01.md) |
| `mortgages_2020_03` | 153 | 2020–2030 | Mortgages | [mortgages_2020_03.md](mortgages_2020_03.md) |
| `mortgages_2021_02` | 153 | 2021–2031 | Mortgages | [mortgages_2021_02.md](mortgages_2021_02.md) |
| `mortgages_2021_07` | 153 | 2021–2031 | Mortgages | [mortgages_2021_07.md](mortgages_2021_07.md) |
| `mortgages_2023_05` | 153 | 2023–2033 | Mortgages | [mortgages_2023_05.md](mortgages_2023_05.md) |
| `mortgages_2024_06` | 153 | 2024–2034 | Mortgages | [mortgages_2024_06.md](mortgages_2024_06.md) |
| `pbgc_2019_05` | 132 | 2018–2029 | PBGC | [pbgc_2019_05.md](pbgc_2019_05.md) |
| `pbgc_2020_01` | 132 | 2019–2030 | PBGC | [pbgc_2020_01.md](pbgc_2020_01.md) |
| `pbgc_2020_03` | 132 | 2019–2030 | PBGC | [pbgc_2020_03.md](pbgc_2020_03.md) |
| `pbgc_2021_02` | 144 | 2020–2031 | PBGC | [pbgc_2021_02.md](pbgc_2021_02.md) |
| `pbgc_2021_07` | 132 | 2020–2031 | PBGC | [pbgc_2021_07.md](pbgc_2021_07.md) |
| `pbgc_2022_05` | 132 | 2021–2032 | PBGC | [pbgc_2022_05.md](pbgc_2022_05.md) |
| `pbgc_2023_05` | 132 | 2022–2033 | PBGC | [pbgc_2023_05.md](pbgc_2023_05.md) |
| `pbgc_2024_06` | 132 | 2023–2034 | PBGC | [pbgc_2024_06.md](pbgc_2024_06.md) |
| `pell_grant_2019_05` | 385 | 2009–2029 | Pell Grant | [pell_grant_2019_05.md](pell_grant_2019_05.md) |
| `pellgrant_0_2020_03` | 372 | 2011–2030 | Pell Grant | [pellgrant_0_2020_03.md](pellgrant_0_2020_03.md) |
| `pellgrant_2020_01` | 393 | 2011–2030 | Pell Grant | [pellgrant_2020_01.md](pellgrant_2020_01.md) |
| `pellgrant_2021_02` | 318 | 2011–2031 | Pell Grant | [pellgrant_2021_02.md](pellgrant_2021_02.md) |
| `pellgrant_2021_07` | 318 | 2011–2031 | Pell Grant | [pellgrant_2021_07.md](pellgrant_2021_07.md) |
| `pellgrant_2022_05` | 318 | 2012–2032 | Pell Grant | [pellgrant_2022_05.md](pellgrant_2022_05.md) |
| `pellgrant_2023_05` | 329 | 2013–2033 | Pell Grant | [pellgrant_2023_05.md](pellgrant_2023_05.md) |
| `pellgrant_2024_06` | 318 | 2014–2034 | Pell Grant | [pellgrant_2024_06.md](pellgrant_2024_06.md) |
| `pellgrant_2025_01` | 350 | 2015–2035 | Pell Grant | [pellgrant_2025_01.md](pellgrant_2025_01.md) |
| `post911_gi_bill_2019_05` | 55 | 2019–2029 | Post-9/11 GI Bill | [post911_gi_bill_2019_05.md](post911_gi_bill_2019_05.md) |
| `post911gibill_2020_01` | 55 | 2020–2030 | Post-9/11 GI Bill | [post911gibill_2020_01.md](post911gibill_2020_01.md) |
| `post911gibill_2020_03` | 55 | 2020–2030 | Post-9/11 GI Bill | [post911gibill_2020_03.md](post911gibill_2020_03.md) |
| `post911gibill_2021_02` | 55 | 2021–2031 | Post-9/11 GI Bill | [post911gibill_2021_02.md](post911gibill_2021_02.md) |
| `post911gibill_2021_07` | 55 | 2021–2031 | Post-9/11 GI Bill | [post911gibill_2021_07.md](post911gibill_2021_07.md) |
| `post911gibill_2022_05` | 55 | 2022–2032 | Post-9/11 GI Bill | [post911gibill_2022_05.md](post911gibill_2022_05.md) |
| `post911gibill_2023_05` | 55 | 2023–2033 | Post-9/11 GI Bill | [post911gibill_2023_05.md](post911gibill_2023_05.md) |
| `post911gibill_2024_02` | 55 | 2024–2034 | Post-9/11 GI Bill | [post911gibill_2024_02.md](post911gibill_2024_02.md) |
| `premium_tax_credit_2024_07` | 33 | 2024–2034 | Premium Tax Credit | [premium_tax_credit_2024_07.md](premium_tax_credit_2024_07.md) |
| `snap_2019_05` | 241 | 2019–2029 | SNAP | [snap_2019_05.md](snap_2019_05.md) |
| `snap_2020_01` | 241 | 2020–2030 | SNAP | [snap_2020_01.md](snap_2020_01.md) |
| `snap_2020_03` | 241 | 2020–2030 | SNAP | [snap_2020_03.md](snap_2020_03.md) |
| `snap_2021_02` | 252 | 2021–2031 | SNAP | [snap_2021_02.md](snap_2021_02.md) |
| `snap_2021_07` | 252 | 2021–2031 | SNAP | [snap_2021_07.md](snap_2021_07.md) |
| `snap_2022_05` | 252 | 2022–2032 | SNAP | [snap_2022_05.md](snap_2022_05.md) |
| `snap_2023_02` | 253 | 2023–2033 | SNAP | [snap_2023_02.md](snap_2023_02.md) |
| `snap_2023_05` | 253 | 2023–2033 | SNAP | [snap_2023_05.md](snap_2023_05.md) |
| `snap_2024_02` | 241 | 2024–2034 | SNAP | [snap_2024_02.md](snap_2024_02.md) |
| `snap_2024_06` | 241 | 2024–2034 | SNAP | [snap_2024_06.md](snap_2024_06.md) |
| `snap_2025_01` | 241 | 2025–2035 | SNAP | [snap_2025_01.md](snap_2025_01.md) |
| `snap_2026_02` | 230 | 2026–2036 | SNAP | [snap_2026_02.md](snap_2026_02.md) |
| `social_security_2019_05` | 392 | 2018–2029 | Social Security | [social_security_2019_05.md](social_security_2019_05.md) |
| `socialsecurity_2020_01` | 393 | 2019–2030 | Social Security | [socialsecurity_2020_01.md](socialsecurity_2020_01.md) |
| `socialsecurity_2020_03` | 405 | 2019–2030 | Social Security | [socialsecurity_2020_03.md](socialsecurity_2020_03.md) |
| `socialsecurity_2021_02` | 393 | 2020–2031 | Social Security | [socialsecurity_2021_02.md](socialsecurity_2021_02.md) |
| `socialsecurity_2021_07` | 393 | 2020–2031 | Social Security | [socialsecurity_2021_07.md](socialsecurity_2021_07.md) |
| `socialsecurity_2022_05` | 395 | 2021–2032 | Social Security | [socialsecurity_2022_05.md](socialsecurity_2022_05.md) |
| `socialsecurity_2023_05` | 371 | 2022–2033 | Social Security | [socialsecurity_2023_05.md](socialsecurity_2023_05.md) |
| `socialsecurity_2024_02` | 366 | 2023–2034 | Social Security | [socialsecurity_2024_02.md](socialsecurity_2024_02.md) |
| `socialsecurity_2024_06` | 369 | 2023–2034 | Social Security | [socialsecurity_2024_06.md](socialsecurity_2024_06.md) |
| `socialsecurity_2025_01` | 368 | 2024–2035 | Social Security | [socialsecurity_2025_01.md](socialsecurity_2025_01.md) |
| `ssdi_2019_05` | 312 | 2018–2029 | SSDI | [ssdi_2019_05.md](ssdi_2019_05.md) |
| `ssdi_2020_01` | 312 | 2019–2030 | SSDI | [ssdi_2020_01.md](ssdi_2020_01.md) |
| `ssdi_2020_03` | 312 | 2019–2030 | SSDI | [ssdi_2020_03.md](ssdi_2020_03.md) |
| `ssdi_2021_02` | 288 | 2020–2031 | SSDI | [ssdi_2021_02.md](ssdi_2021_02.md) |
| `ssdi_2021_07` | 288 | 2020–2031 | SSDI | [ssdi_2021_07.md](ssdi_2021_07.md) |
| `ssdi_2022_05` | 288 | 2021–2032 | SSDI | [ssdi_2022_05.md](ssdi_2022_05.md) |
| `ssdi_2023_05` | 288 | 2022–2033 | SSDI | [ssdi_2023_05.md](ssdi_2023_05.md) |
| `ssdi_2024_02` | 288 | 2023–2034 | SSDI | [ssdi_2024_02.md](ssdi_2024_02.md) |
| `ssdi_2024_06` | 288 | 2023–2034 | SSDI | [ssdi_2024_06.md](ssdi_2024_06.md) |
| `ssdi_2025_01` | 288 | 2024–2035 | SSDI | [ssdi_2025_01.md](ssdi_2025_01.md) |
| `ssdi_2026_02` | 288 | 2025–2036 | SSDI | [ssdi_2026_02.md](ssdi_2026_02.md) |
| `ssi_1_2020_01` | 242 | 2020–2030 | SSI | [ssi_1_2020_01.md](ssi_1_2020_01.md) |
| `ssi_2019_05` | 264 | 2018–2029 | SSI | [ssi_2019_05.md](ssi_2019_05.md) |
| `ssi_2020_03` | 242 | 2020–2030 | SSI | [ssi_2020_03.md](ssi_2020_03.md) |
| `ssi_2021_02` | 110 | 2021–2031 | SSI | [ssi_2021_02.md](ssi_2021_02.md) |
| `ssi_2021_07` | 110 | 2021–2031 | SSI | [ssi_2021_07.md](ssi_2021_07.md) |
| `ssi_2022_05` | 110 | 2022–2032 | SSI | [ssi_2022_05.md](ssi_2022_05.md) |
| `ssi_2023_05` | 110 | 2023–2033 | SSI | [ssi_2023_05.md](ssi_2023_05.md) |
| `ssi_2024_02` | 110 | 2024–2034 | SSI | [ssi_2024_02.md](ssi_2024_02.md) |
| `ssi_2024_06` | 110 | 2024–2034 | SSI | [ssi_2024_06.md](ssi_2024_06.md) |
| `ssi_2025_01` | 132 | 2025–2035 | SSI | [ssi_2025_01.md](ssi_2025_01.md) |
| `sstrustfund_2021_02` | 204 | 2020–2031 | Social Security Trust Funds | [sstrustfund_2021_02.md](sstrustfund_2021_02.md) |
| `student_loan_2019_05` | 924 | 2019–2029 | Student Loans | [student_loan_2019_05.md](student_loan_2019_05.md) |
| `studentloan_2020_03` | 1,037 | 2013–2030 | Student Loans | [studentloan_2020_03.md](studentloan_2020_03.md) |
| `studentloan_2021_07` | 935 | 2021–2031 | Student Loans | [studentloan_2021_07.md](studentloan_2021_07.md) |
| `studentloan_2022_05` | 941 | 2020–2032 | Student Loans | [studentloan_2022_05.md](studentloan_2022_05.md) |
| `studentloan_2023_05` | 913 | 2023–2033 | Student Loans | [studentloan_2023_05.md](studentloan_2023_05.md) |
| `studentloan_2024_06` | 826 | 2024–2034 | Student Loans | [studentloan_2024_06.md](studentloan_2024_06.md) |
| `tanf_2019_05` | 88 | 2019–2029 | TANF | [tanf_2019_05.md](tanf_2019_05.md) |
| `tanf_2020_01` | 99 | 2020–2030 | TANF | [tanf_2020_01.md](tanf_2020_01.md) |
| `tanf_2020_03` | 88 | 2020–2030 | TANF | [tanf_2020_03.md](tanf_2020_03.md) |
| `tanf_2021_02` | 88 | 2021–2031 | TANF | [tanf_2021_02.md](tanf_2021_02.md) |
| `tanf_2021_07` | 99 | 2021–2031 | TANF | [tanf_2021_07.md](tanf_2021_07.md) |
| `tanf_2022_05` | 88 | 2022–2032 | TANF | [tanf_2022_05.md](tanf_2022_05.md) |
| `tanf_2023_05` | 88 | 2023–2033 | TANF | [tanf_2023_05.md](tanf_2023_05.md) |
| `tanf_2024_02` | 88 | 2024–2034 | TANF | [tanf_2024_02.md](tanf_2024_02.md) |
| `tanf_2024_06` | 87 | 2024–2034 | TANF | [tanf_2024_06.md](tanf_2024_06.md) |
| `tanf_2025_01` | 87 | 2025–2035 | TANF | [tanf_2025_01.md](tanf_2025_01.md) |
| `tanf_2026_02` | 88 | 2026–2036 | TANF | [tanf_2026_02.md](tanf_2026_02.md) |
| `tef_2024_06` | 221 | 2024–2034 | Toxic Exposures Fund | [tef_2024_06.md](tef_2024_06.md) |
| `tef_2025_01` | 221 | 2025–2035 | Toxic Exposures Fund | [tef_2025_01.md](tef_2025_01.md) |
| `toxic_exposures_fund_2024_02` | 221 | 2024–2034 | Toxic Exposures Fund | [toxic_exposures_fund_2024_02.md](toxic_exposures_fund_2024_02.md) |
| `trust_funds_2019_05` | 228 | 2018–2029 | Social Security Trust Funds | [trust_funds_2019_05.md](trust_funds_2019_05.md) |
| `trustfund_2020_01` | 204 | 2019–2030 | Social Security Trust Funds | [trustfund_2020_01.md](trustfund_2020_01.md) |
| `trustfund_2020_03` | 204 | 2019–2030 | Social Security Trust Funds | [trustfund_2020_03.md](trustfund_2020_03.md) |
| `trustfund_2021_07` | 200 | 2020–2031 | Social Security Trust Funds | [trustfund_2021_07.md](trustfund_2021_07.md) |
| `trustfund_2022_05` | 234 | 2021–2032 | Social Security Trust Funds | [trustfund_2022_05.md](trustfund_2022_05.md) |
| `trustfund_2023_05` | 254 | 2022–2033 | Social Security Trust Funds | [trustfund_2023_05.md](trustfund_2023_05.md) |
| `trustfund_2024_02` | 254 | 2023–2034 | Social Security Trust Funds | [trustfund_2024_02.md](trustfund_2024_02.md) |
| `trustfund_2024_06` | 254 | 2023–2034 | Social Security Trust Funds | [trustfund_2024_06.md](trustfund_2024_06.md) |
| `trustfund_2025_01` | 253 | 2024–2035 | Social Security Trust Funds | [trustfund_2025_01.md](trustfund_2025_01.md) |
| `unemployment_2019_05` | 99 | 2019–2029 | Unemployment Insurance | [unemployment_2019_05.md](unemployment_2019_05.md) |
| `unemployment_2020_01` | 99 | 2020–2030 | Unemployment Insurance | [unemployment_2020_01.md](unemployment_2020_01.md) |
| `unemployment_2020_03` | 99 | 2020–2030 | Unemployment Insurance | [unemployment_2020_03.md](unemployment_2020_03.md) |
| `unemployment_2021_02` | 209 | 2021–2031 | Unemployment Insurance | [unemployment_2021_02.md](unemployment_2021_02.md) |
| `unemployment_2021_07` | 209 | 2021–2031 | Unemployment Insurance | [unemployment_2021_07.md](unemployment_2021_07.md) |
| `unemployment_2022_05` | 209 | 2022–2032 | Unemployment Insurance | [unemployment_2022_05.md](unemployment_2022_05.md) |
| `unemployment_2023_05` | 143 | 2023–2033 | Unemployment Insurance | [unemployment_2023_05.md](unemployment_2023_05.md) |
| `unemployment_2024_02` | 143 | 2024–2034 | Unemployment Insurance | [unemployment_2024_02.md](unemployment_2024_02.md) |
| `unemployment_2024_06` | 143 | 2024–2034 | Unemployment Insurance | [unemployment_2024_06.md](unemployment_2024_06.md) |
| `unemployment_2025_01` | 99 | 2025–2035 | Unemployment Insurance | [unemployment_2025_01.md](unemployment_2025_01.md) |
| `unemployment_2026_02` | 99 | 2026–2036 | Unemployment Insurance | [unemployment_2026_02.md](unemployment_2026_02.md) |
| `usda_2020_01` | 10,897 | 2018–2030 | USDA Farm Programs | [usda_2020_01.md](usda_2020_01.md) |
| `usda_2020_03` | 10,945 | 2018–2030 | USDA Farm Programs | [usda_2020_03.md](usda_2020_03.md) |
| `usda_2021_02` | 10,990 | 2019–2031 | USDA Farm Programs | [usda_2021_02.md](usda_2021_02.md) |
| `usda_2021_07` | 10,978 | 2019–2031 | USDA Farm Programs | [usda_2021_07.md](usda_2021_07.md) |
| `usda_2022_05` | 10,890 | 1901–2032 | USDA Farm Programs | [usda_2022_05.md](usda_2022_05.md) |
| `usda_2023_02` | 11,002 | 2021–2033 | USDA Farm Programs | [usda_2023_02.md](usda_2023_02.md) |
| `usda_2023_05` | 11,394 | 2021–2033 | USDA Farm Programs | [usda_2023_05.md](usda_2023_05.md) |
| `usda_2024_02` | 11,373 | 2022–2034 | USDA Farm Programs | [usda_2024_02.md](usda_2024_02.md) |
| `usda_2024_06` | 11,734 | 2022–2034 | USDA Farm Programs | [usda_2024_06.md](usda_2024_06.md) |
| `usda_2025_01` | 11,155 | 1963–2041 | USDA Farm Programs | [usda_2025_01.md](usda_2025_01.md) |
| `veterans_2019_05` | 242 | 2019–2029 | Veterans Benefits | [veterans_2019_05.md](veterans_2019_05.md) |
| `veteransbenefit_2020_01` | 242 | 2020–2030 | Veterans Benefits | [veteransbenefit_2020_01.md](veteransbenefit_2020_01.md) |
| `veteransbenefit_2020_03` | 242 | 2020–2030 | Veterans Benefits | [veteransbenefit_2020_03.md](veteransbenefit_2020_03.md) |
| `veteransbenefit_2021_02` | 242 | 2021–2031 | Veterans Benefits | [veteransbenefit_2021_02.md](veteransbenefit_2021_02.md) |
| `veteransbenefit_2022_05` | 132 | 2022–2032 | Veterans Benefits | [veteransbenefit_2022_05.md](veteransbenefit_2022_05.md) |
| `veteransbenefit_2023_05` | 132 | 2023–2033 | Veterans Benefits | [veteransbenefit_2023_05.md](veteransbenefit_2023_05.md) |
| `veteransbenefit_2024_02` | 132 | 2024–2034 | Veterans Benefits | [veteransbenefit_2024_02.md](veteransbenefit_2024_02.md) |
| `veteransbenefit_2025_01` | 176 | 2025–2035 | Veterans Benefits | [veteransbenefit_2025_01.md](veteransbenefit_2025_01.md) |
