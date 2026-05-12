# CBO Baseline Dataset Schemas

One schema document exists for every processed CSV in `data/processed/`. Each file documents column definitions, provenance, and aggregation caveats.

**Total datasets:** 222

## Column reference (all datasets share this schema)

| Column | Type | Description | Unit | Example | Notes |
|---|---|---|---|---|---|
| `program` | string | CBO program name inferred from the source workbook filename. | N/A | — | Derived from the workbook filename; may include a version suffix for older files. |
| `category` | string | Line-item label as it appears in the source worksheet after header normalization. | N/A | — | Rows where ``is_total`` is ``true`` represent aggregated totals or subtotals and should be excluded from sum-based aggregations to avoid double-counting. |
| `fiscal_year` | integer | Federal fiscal year to which the value applies (Oct 1 – Sep 30). | Year | — | Only years in the range 2019–2040 are included; historical prior-year columns outside that range are silently dropped by the transform. |
| `value` | float | Parsed numeric value from the source cell. | See ``unit`` column | — | Negative values indicate outflows or reductions. Values originally enclosed in parentheses (e.g. ``(123)``) are converted to negative floats. |
| `unit` | string | Unit of measure for the ``value`` column, sourced from the parse plan. | N/A | — | Common values include 'Millions of dollars', 'Billions of dollars', and 'Thousands'. |
| `source_file` | string | Original CBO workbook filename from ``data/raw/``. | N/A | — | Use this column to trace any row back to its exact source workbook. |
| `source_sheet` | string | Worksheet name within the source workbook. | N/A | — | Combine with ``source_file`` for a fully qualified provenance reference. |
| `is_total` | boolean | ``true`` if the category label contains the word 'total' or 'subtotal', indicating an aggregated row. | N/A | — | **Always filter ``is_total = true`` rows out before computing sums or averages** across categories to avoid double-counting. Retain them for headline/summary views. |

## Dataset index

| Dataset | Rows | Fiscal years | Programs | Schema |
|---|---|---|---|---|
| `aatf_0_2023_05` | 231 | 2023–2033 | Aatf 0 | [aatf_0_2023_05.md](aatf_0_2023_05.md) |
| `aatf_2024_02` | 231 | 2024–2034 | Aatf | [aatf_2024_02.md](aatf_2024_02.md) |
| `aatf_2024_06` | 231 | 2024–2034 | Aatf | [aatf_2024_06.md](aatf_2024_06.md) |
| `aatf_2025_01` | 209 | 2025–2035 | Aatf | [aatf_2025_01.md](aatf_2025_01.md) |
| `aatf_2026_02` | 209 | 2026–2036 | Aatf | [aatf_2026_02.md](aatf_2026_02.md) |
| `child_nutrition_2019_05` | 102 | 2019–2024 | Child Nutrition | [child_nutrition_2019_05.md](child_nutrition_2019_05.md) |
| `child_support_enforcement_2019_05` | 55 | 2019–2029 | Child Support Enforcement | [child_support_enforcement_2019_05.md](child_support_enforcement_2019_05.md) |
| `childnutrition_0_2022_05` | 186 | 2022–2032 | Childnutrition 0 | [childnutrition_0_2022_05.md](childnutrition_0_2022_05.md) |
| `childnutrition_0_2024_02` | 218 | 2024–2034 | Childnutrition 0 | [childnutrition_0_2024_02.md](childnutrition_0_2024_02.md) |
| `childnutrition_2020_01` | 121 | 2020–2030 | Childnutrition | [childnutrition_2020_01.md](childnutrition_2020_01.md) |
| `childnutrition_2020_03` | 121 | 2020–2030 | Childnutrition | [childnutrition_2020_03.md](childnutrition_2020_03.md) |
| `childnutrition_2021_02` | 176 | 2021–2031 | Childnutrition | [childnutrition_2021_02.md](childnutrition_2021_02.md) |
| `childnutrition_2021_07` | 176 | 2021–2031 | Childnutrition | [childnutrition_2021_07.md](childnutrition_2021_07.md) |
| `childnutrition_2023_05` | 186 | 2023–2033 | Childnutrition | [childnutrition_2023_05.md](childnutrition_2023_05.md) |
| `childnutrition_2024_06` | 218 | 2024–2034 | Childnutrition | [childnutrition_2024_06.md](childnutrition_2024_06.md) |
| `childnutrition_2025_01` | 218 | 2025–2035 | Childnutrition | [childnutrition_2025_01.md](childnutrition_2025_01.md) |
| `childsupportenforcement_2020_01` | 55 | 2020–2030 | Childsupportenforcement | [childsupportenforcement_2020_01.md](childsupportenforcement_2020_01.md) |
| `childsupportenforcement_2020_03` | 55 | 2020–2030 | Childsupportenforcement | [childsupportenforcement_2020_03.md](childsupportenforcement_2020_03.md) |
| `childsupportenforcement_2021_02` | 88 | 2021–2031 | Childsupportenforcement | [childsupportenforcement_2021_02.md](childsupportenforcement_2021_02.md) |
| `childsupportenforcement_2021_07` | 44 | 2021–2031 | Childsupportenforcement | [childsupportenforcement_2021_07.md](childsupportenforcement_2021_07.md) |
| `chip_2019_05` | 139 | 2019–2029 | Chip | [chip_2019_05.md](chip_2019_05.md) |
| `chip_2020_03` | 138 | 2019–2030 | Chip | [chip_2020_03.md](chip_2020_03.md) |
| `chip_2021_07` | 99 | 2021–2031 | Chip | [chip_2021_07.md](chip_2021_07.md) |
| `chip_2022_05` | 108 | 2021–2032 | Chip | [chip_2022_05.md](chip_2022_05.md) |
| `chip_2023_05` | 108 | 2022–2033 | Chip | [chip_2023_05.md](chip_2023_05.md) |
| `chip_2024_06` | 99 | 2024–2034 | Chip | [chip_2024_06.md](chip_2024_06.md) |
| `chip_2026_02` | 55 | 2026–2036 | Chip | [chip_2026_02.md](chip_2026_02.md) |
| `csec_0_2022_05` | 55 | 2022–2032 | Csec 0 | [csec_0_2022_05.md](csec_0_2022_05.md) |
| `csec_2023_05` | 55 | 2023–2033 | Csec | [csec_2023_05.md](csec_2023_05.md) |
| `csec_2024_02` | 55 | 2024–2034 | Csec | [csec_2024_02.md](csec_2024_02.md) |
| `csec_2024_06` | 54 | 2024–2034 | Csec | [csec_2024_06.md](csec_2024_06.md) |
| `csec_2025_01` | 65 | 2025–2035 | Csec | [csec_2025_01.md](csec_2025_01.md) |
| `customs_fees_2025_01` | 48 | 2025–2035 | Customs Fees | [customs_fees_2025_01.md](customs_fees_2025_01.md) |
| `dodmedicare_2019_05` | 132 | 2019–2029 | Dodmedicare | [dodmedicare_2019_05.md](dodmedicare_2019_05.md) |
| `dodmedicare_2020_01` | 132 | 2020–2030 | Dodmedicare | [dodmedicare_2020_01.md](dodmedicare_2020_01.md) |
| `dodmedicare_2020_03` | 132 | 2020–2030 | Dodmedicare | [dodmedicare_2020_03.md](dodmedicare_2020_03.md) |
| `dodmedicare_2021_02` | 121 | 2021–2031 | Dodmedicare | [dodmedicare_2021_02.md](dodmedicare_2021_02.md) |
| `dodmedicare_2021_07` | 121 | 2021–2031 | Dodmedicare | [dodmedicare_2021_07.md](dodmedicare_2021_07.md) |
| `dodmedicare_2022_05` | 121 | 2022–2032 | Dodmedicare | [dodmedicare_2022_05.md](dodmedicare_2022_05.md) |
| `dodmedicare_2023_05` | 121 | 2023–2033 | Dodmedicare | [dodmedicare_2023_05.md](dodmedicare_2023_05.md) |
| `dodmedicare_2024_02` | 121 | 2024–2034 | Dodmedicare | [dodmedicare_2024_02.md](dodmedicare_2024_02.md) |
| `dodmedicare_2025_01` | 121 | 2025–2035 | Dodmedicare | [dodmedicare_2025_01.md](dodmedicare_2025_01.md) |
| `fdic_2024_06` | 60 | 2023–2034 | Fdic | [fdic_2024_06.md](fdic_2024_06.md) |
| `fdic_2025_01` | 52 | 2023–2035 | Fdic | [fdic_2025_01.md](fdic_2025_01.md) |
| `foster_care_2019_05` | 264 | 2019–2029 | Foster Care | [foster_care_2019_05.md](foster_care_2019_05.md) |
| `fostercare_2020_01` | 275 | 2020–2030 | Fostercare | [fostercare_2020_01.md](fostercare_2020_01.md) |
| `fostercare_2020_03` | 275 | 2020–2030 | Fostercare | [fostercare_2020_03.md](fostercare_2020_03.md) |
| `fostercare_2021_02` | 275 | 2021–2031 | Fostercare | [fostercare_2021_02.md](fostercare_2021_02.md) |
| `fostercare_2021_07` | 275 | 2021–2031 | Fostercare | [fostercare_2021_07.md](fostercare_2021_07.md) |
| `fostercare_2022_05` | 253 | 2022–2032 | Fostercare | [fostercare_2022_05.md](fostercare_2022_05.md) |
| `fostercare_2023_05` | 253 | 2023–2033 | Fostercare | [fostercare_2023_05.md](fostercare_2023_05.md) |
| `fostercare_2024_02` | 253 | 2024–2034 | Fostercare | [fostercare_2024_02.md](fostercare_2024_02.md) |
| `fostercare_2024_06` | 253 | 2024–2034 | Fostercare | [fostercare_2024_06.md](fostercare_2024_06.md) |
| `fostercare_2025_01` | 253 | 2025–2035 | Fostercare | [fostercare_2025_01.md](fostercare_2025_01.md) |
| `fostercare_2026_02` | 253 | 2026–2036 | Fostercare | [fostercare_2026_02.md](fostercare_2026_02.md) |
| `health_insurance_2019_05` | 1,065 | 2019–2029 | Health Insurance | [health_insurance_2019_05.md](health_insurance_2019_05.md) |
| `healthinsurance_2020_03` | 1,034 | 2019–2030 | Healthinsurance | [healthinsurance_2020_03.md](healthinsurance_2020_03.md) |
| `healthinsurance_2020_09` | 1,065 | 2019–2030 | Healthinsurance | [healthinsurance_2020_09.md](healthinsurance_2020_09.md) |
| `healthinsurance_2021_07` | 473 | 2021–2031 | Healthinsurance | [healthinsurance_2021_07.md](healthinsurance_2021_07.md) |
| `healthinsurance_2022_06` | 472 | 2022–2032 | Healthinsurance | [healthinsurance_2022_06.md](healthinsurance_2022_06.md) |
| `healthinsurance_2023_05` | 440 | 2023–2033 | Healthinsurance | [healthinsurance_2023_05.md](healthinsurance_2023_05.md) |
| `healthinsurance_2023_09` | 473 | 2023–2033 | Healthinsurance | [healthinsurance_2023_09.md](healthinsurance_2023_09.md) |
| `healthinsurance_2024_06` | 507 | 2023–2034 | Healthinsurance | [healthinsurance_2024_06.md](healthinsurance_2024_06.md) |
| `highway_trust_fund_2019_05` | 96 | 2019–2029 | Highway Trust Fund | [highway_trust_fund_2019_05.md](highway_trust_fund_2019_05.md) |
| `highwaytrustfund_2020_01` | 103 | 2019–2030 | Highwaytrustfund | [highwaytrustfund_2020_01.md](highwaytrustfund_2020_01.md) |
| `highwaytrustfund_2020_03` | 103 | 2019–2030 | Highwaytrustfund | [highwaytrustfund_2020_03.md](highwaytrustfund_2020_03.md) |
| `highwaytrustfund_2021_02` | 126 | 2020–2031 | Highwaytrustfund | [highwaytrustfund_2021_02.md](highwaytrustfund_2021_02.md) |
| `highwaytrustfund_2021_07` | 127 | 2020–2031 | Highwaytrustfund | [highwaytrustfund_2021_07.md](highwaytrustfund_2021_07.md) |
| `highwaytrustfund_2022_05` | 134 | 2021–2032 | Highwaytrustfund | [highwaytrustfund_2022_05.md](highwaytrustfund_2022_05.md) |
| `highwaytrustfund_2023_05` | 134 | 2022–2033 | Highwaytrustfund | [highwaytrustfund_2023_05.md](highwaytrustfund_2023_05.md) |
| `highwaytrustfund_2024_02` | 108 | 2023–2034 | Highwaytrustfund | [highwaytrustfund_2024_02.md](highwaytrustfund_2024_02.md) |
| `highwaytrustfund_2024_06` | 108 | 2023–2034 | Highwaytrustfund | [highwaytrustfund_2024_06.md](highwaytrustfund_2024_06.md) |
| `highwaytrustfund_2025_01` | 116 | 2024–2035 | Highwaytrustfund | [highwaytrustfund_2025_01.md](highwaytrustfund_2025_01.md) |
| `medicaid_2019_05` | 242 | 2019–2029 | Medicaid | [medicaid_2019_05.md](medicaid_2019_05.md) |
| `medicaid_2020_03` | 258 | 2019–2030 | Medicaid | [medicaid_2020_03.md](medicaid_2020_03.md) |
| `medicaid_2021_07` | 312 | 2020–2031 | Medicaid | [medicaid_2021_07.md](medicaid_2021_07.md) |
| `medicaid_2022_05` | 336 | 2021–2032 | Medicaid | [medicaid_2022_05.md](medicaid_2022_05.md) |
| `medicaid_2023_05` | 336 | 2022–2033 | Medicaid | [medicaid_2023_05.md](medicaid_2023_05.md) |
| `medicaid_2024_06` | 308 | 2024–2034 | Medicaid | [medicaid_2024_06.md](medicaid_2024_06.md) |
| `medicaid_2026_02` | 336 | 2025–2036 | Medicaid | [medicaid_2026_02.md](medicaid_2026_02.md) |
| `medicare_2019_05` | 598 | 2019–2029 | Medicare | [medicare_2019_05.md](medicare_2019_05.md) |
| `medicare_2020_03` | 687 | 2019–2030 | Medicare | [medicare_2020_03.md](medicare_2020_03.md) |
| `medicare_2021_07` | 495 | 2020–2031 | Medicare | [medicare_2021_07.md](medicare_2021_07.md) |
| `medicare_2022_05` | 511 | 2021–2032 | Medicare | [medicare_2022_05.md](medicare_2022_05.md) |
| `medicare_2023_05` | 528 | 2022–2033 | Medicare | [medicare_2023_05.md](medicare_2023_05.md) |
| `medicare_2024_06` | 516 | 2023–2034 | Medicare | [medicare_2024_06.md](medicare_2024_06.md) |
| `medicare_2026_02` | 516 | 2025–2036 | Medicare | [medicare_2026_02.md](medicare_2026_02.md) |
| `military_retirement_2019_05` | 99 | 2019–2029 | Military Retirement | [military_retirement_2019_05.md](military_retirement_2019_05.md) |
| `militaryretirement_0_2022_05` | 96 | 2022–2032 | Militaryretirement 0 | [militaryretirement_0_2022_05.md](militaryretirement_0_2022_05.md) |
| `militaryretirement_2020_01` | 99 | 2020–2030 | Militaryretirement | [militaryretirement_2020_01.md](militaryretirement_2020_01.md) |
| `militaryretirement_2020_03` | 99 | 2020–2030 | Militaryretirement | [militaryretirement_2020_03.md](militaryretirement_2020_03.md) |
| `militaryretirement_2021_02` | 88 | 2021–2031 | Militaryretirement | [militaryretirement_2021_02.md](militaryretirement_2021_02.md) |
| `militaryretirement_2023_05` | 96 | 2023–2033 | Militaryretirement | [militaryretirement_2023_05.md](militaryretirement_2023_05.md) |
| `militaryretirement_2024_06` | 96 | 2024–2034 | Militaryretirement | [militaryretirement_2024_06.md](militaryretirement_2024_06.md) |
| `mortgages_0_2022_05` | 153 | 2022–2032 | Mortgages 0 | [mortgages_0_2022_05.md](mortgages_0_2022_05.md) |
| `mortgages_2019_05` | 153 | 2019–2029 | Mortgages | [mortgages_2019_05.md](mortgages_2019_05.md) |
| `mortgages_2020_01` | 153 | 2020–2030 | Mortgages | [mortgages_2020_01.md](mortgages_2020_01.md) |
| `mortgages_2020_03` | 153 | 2020–2030 | Mortgages | [mortgages_2020_03.md](mortgages_2020_03.md) |
| `mortgages_2021_02` | 153 | 2021–2031 | Mortgages | [mortgages_2021_02.md](mortgages_2021_02.md) |
| `mortgages_2021_07` | 153 | 2021–2031 | Mortgages | [mortgages_2021_07.md](mortgages_2021_07.md) |
| `mortgages_2023_05` | 153 | 2023–2033 | Mortgages | [mortgages_2023_05.md](mortgages_2023_05.md) |
| `mortgages_2024_06` | 153 | 2024–2034 | Mortgages | [mortgages_2024_06.md](mortgages_2024_06.md) |
| `pbgc_2019_05` | 132 | 2019–2029 | Pbgc | [pbgc_2019_05.md](pbgc_2019_05.md) |
| `pbgc_2020_01` | 144 | 2019–2030 | Pbgc | [pbgc_2020_01.md](pbgc_2020_01.md) |
| `pbgc_2020_03` | 144 | 2019–2030 | Pbgc | [pbgc_2020_03.md](pbgc_2020_03.md) |
| `pbgc_2021_02` | 144 | 2020–2031 | Pbgc | [pbgc_2021_02.md](pbgc_2021_02.md) |
| `pbgc_2021_07` | 132 | 2020–2031 | Pbgc | [pbgc_2021_07.md](pbgc_2021_07.md) |
| `pbgc_2022_05` | 132 | 2021–2032 | Pbgc | [pbgc_2022_05.md](pbgc_2022_05.md) |
| `pbgc_2023_05` | 132 | 2022–2033 | Pbgc | [pbgc_2023_05.md](pbgc_2023_05.md) |
| `pbgc_2024_06` | 132 | 2023–2034 | Pbgc | [pbgc_2024_06.md](pbgc_2024_06.md) |
| `pell_grant_2019_05` | 244 | 2019–2029 | Pell Grant | [pell_grant_2019_05.md](pell_grant_2019_05.md) |
| `pellgrant_0_2020_03` | 251 | 2019–2030 | Pellgrant 0 | [pellgrant_0_2020_03.md](pellgrant_0_2020_03.md) |
| `pellgrant_2020_01` | 253 | 2019–2030 | Pellgrant | [pellgrant_2020_01.md](pellgrant_2020_01.md) |
| `pellgrant_2021_02` | 87 | 2019–2021 | Pellgrant | [pellgrant_2021_02.md](pellgrant_2021_02.md) |
| `pellgrant_2021_07` | 87 | 2019–2021 | Pellgrant | [pellgrant_2021_07.md](pellgrant_2021_07.md) |
| `pellgrant_2022_05` | 116 | 2019–2022 | Pellgrant | [pellgrant_2022_05.md](pellgrant_2022_05.md) |
| `pellgrant_2023_05` | 150 | 2019–2023 | Pellgrant | [pellgrant_2023_05.md](pellgrant_2023_05.md) |
| `pellgrant_2024_06` | 174 | 2019–2024 | Pellgrant | [pellgrant_2024_06.md](pellgrant_2024_06.md) |
| `pellgrant_2025_01` | 277 | 2019–2035 | Pellgrant | [pellgrant_2025_01.md](pellgrant_2025_01.md) |
| `post911_gi_bill_2019_05` | 55 | 2019–2029 | Post911 Gi Bill | [post911_gi_bill_2019_05.md](post911_gi_bill_2019_05.md) |
| `post911gibill_2020_01` | 55 | 2020–2030 | Post911Gibill | [post911gibill_2020_01.md](post911gibill_2020_01.md) |
| `post911gibill_2020_03` | 55 | 2020–2030 | Post911Gibill | [post911gibill_2020_03.md](post911gibill_2020_03.md) |
| `post911gibill_2021_02` | 55 | 2021–2031 | Post911Gibill | [post911gibill_2021_02.md](post911gibill_2021_02.md) |
| `post911gibill_2021_07` | 55 | 2021–2031 | Post911Gibill | [post911gibill_2021_07.md](post911gibill_2021_07.md) |
| `post911gibill_2022_05` | 55 | 2022–2032 | Post911Gibill | [post911gibill_2022_05.md](post911gibill_2022_05.md) |
| `post911gibill_2023_05` | 55 | 2023–2033 | Post911Gibill | [post911gibill_2023_05.md](post911gibill_2023_05.md) |
| `post911gibill_2024_02` | 55 | 2024–2034 | Post911Gibill | [post911gibill_2024_02.md](post911gibill_2024_02.md) |
| `premium_tax_credit_2024_07` | 33 | 2024–2034 | Premium Tax Credit | [premium_tax_credit_2024_07.md](premium_tax_credit_2024_07.md) |
| `snap_2019_05` | 252 | 2019–2029 | Snap | [snap_2019_05.md](snap_2019_05.md) |
| `snap_2020_01` | 252 | 2020–2030 | Snap | [snap_2020_01.md](snap_2020_01.md) |
| `snap_2020_03` | 252 | 2020–2030 | Snap | [snap_2020_03.md](snap_2020_03.md) |
| `snap_2021_02` | 252 | 2021–2031 | Snap | [snap_2021_02.md](snap_2021_02.md) |
| `snap_2021_07` | 252 | 2021–2031 | Snap | [snap_2021_07.md](snap_2021_07.md) |
| `snap_2022_05` | 252 | 2022–2032 | Snap | [snap_2022_05.md](snap_2022_05.md) |
| `snap_2023_02` | 253 | 2023–2033 | Snap | [snap_2023_02.md](snap_2023_02.md) |
| `snap_2023_05` | 253 | 2023–2033 | Snap | [snap_2023_05.md](snap_2023_05.md) |
| `snap_2024_02` | 241 | 2024–2034 | Snap | [snap_2024_02.md](snap_2024_02.md) |
| `snap_2024_06` | 241 | 2024–2034 | Snap | [snap_2024_06.md](snap_2024_06.md) |
| `snap_2025_01` | 241 | 2025–2035 | Snap | [snap_2025_01.md](snap_2025_01.md) |
| `snap_2026_02` | 230 | 2026–2036 | Snap | [snap_2026_02.md](snap_2026_02.md) |
| `social_security_2019_05` | 371 | 2019–2029 | Social Security | [social_security_2019_05.md](social_security_2019_05.md) |
| `socialsecurity_2020_01` | 405 | 2019–2030 | Socialsecurity | [socialsecurity_2020_01.md](socialsecurity_2020_01.md) |
| `socialsecurity_2020_03` | 417 | 2019–2030 | Socialsecurity | [socialsecurity_2020_03.md](socialsecurity_2020_03.md) |
| `socialsecurity_2021_02` | 393 | 2020–2031 | Socialsecurity. | [socialsecurity_2021_02.md](socialsecurity_2021_02.md) |
| `socialsecurity_2021_07` | 393 | 2020–2031 | Socialsecurity | [socialsecurity_2021_07.md](socialsecurity_2021_07.md) |
| `socialsecurity_2022_05` | 395 | 2021–2032 | Socialsecurity | [socialsecurity_2022_05.md](socialsecurity_2022_05.md) |
| `socialsecurity_2023_05` | 371 | 2022–2033 | Socialsecurity | [socialsecurity_2023_05.md](socialsecurity_2023_05.md) |
| `socialsecurity_2024_02` | 366 | 2023–2034 | Socialsecurity | [socialsecurity_2024_02.md](socialsecurity_2024_02.md) |
| `socialsecurity_2024_06` | 369 | 2023–2034 | Socialsecurity | [socialsecurity_2024_06.md](socialsecurity_2024_06.md) |
| `socialsecurity_2025_01` | 368 | 2024–2035 | Socialsecurity | [socialsecurity_2025_01.md](socialsecurity_2025_01.md) |
| `ssdi_2019_05` | 286 | 2019–2029 | Ssdi | [ssdi_2019_05.md](ssdi_2019_05.md) |
| `ssdi_2020_01` | 312 | 2019–2030 | Ssdi | [ssdi_2020_01.md](ssdi_2020_01.md) |
| `ssdi_2020_03` | 312 | 2019–2030 | Ssdi | [ssdi_2020_03.md](ssdi_2020_03.md) |
| `ssdi_2021_02` | 288 | 2020–2031 | Ssdi. | [ssdi_2021_02.md](ssdi_2021_02.md) |
| `ssdi_2021_07` | 288 | 2020–2031 | Ssdi | [ssdi_2021_07.md](ssdi_2021_07.md) |
| `ssdi_2022_05` | 288 | 2021–2032 | Ssdi | [ssdi_2022_05.md](ssdi_2022_05.md) |
| `ssdi_2023_05` | 288 | 2022–2033 | Ssdi | [ssdi_2023_05.md](ssdi_2023_05.md) |
| `ssdi_2024_02` | 288 | 2023–2034 | Ssdi | [ssdi_2024_02.md](ssdi_2024_02.md) |
| `ssdi_2024_06` | 288 | 2023–2034 | Ssdi | [ssdi_2024_06.md](ssdi_2024_06.md) |
| `ssdi_2025_01` | 288 | 2024–2035 | Ssdi | [ssdi_2025_01.md](ssdi_2025_01.md) |
| `ssdi_2026_02` | 288 | 2025–2036 | Ssdi | [ssdi_2026_02.md](ssdi_2026_02.md) |
| `ssi_1_2020_01` | 242 | 2020–2030 | Ssi 1 | [ssi_1_2020_01.md](ssi_1_2020_01.md) |
| `ssi_2019_05` | 242 | 2019–2029 | Ssi | [ssi_2019_05.md](ssi_2019_05.md) |
| `ssi_2020_03` | 242 | 2020–2030 | Ssi | [ssi_2020_03.md](ssi_2020_03.md) |
| `ssi_2021_02` | 110 | 2021–2031 | Ssi | [ssi_2021_02.md](ssi_2021_02.md) |
| `ssi_2021_07` | 110 | 2021–2031 | Ssi | [ssi_2021_07.md](ssi_2021_07.md) |
| `ssi_2022_05` | 110 | 2022–2032 | Ssi | [ssi_2022_05.md](ssi_2022_05.md) |
| `ssi_2023_05` | 110 | 2023–2033 | Ssi | [ssi_2023_05.md](ssi_2023_05.md) |
| `ssi_2024_02` | 110 | 2024–2034 | Ssi | [ssi_2024_02.md](ssi_2024_02.md) |
| `ssi_2024_06` | 110 | 2024–2034 | Ssi | [ssi_2024_06.md](ssi_2024_06.md) |
| `ssi_2025_01` | 132 | 2025–2035 | Ssi | [ssi_2025_01.md](ssi_2025_01.md) |
| `sstrustfund_2021_02` | 180 | 2020–2031 | Sstrustfund | [sstrustfund_2021_02.md](sstrustfund_2021_02.md) |
| `student_loan_2019_05` | 638 | 2019–2029 | Student Loan | [student_loan_2019_05.md](student_loan_2019_05.md) |
| `studentloan_2020_03` | 792 | 2020–2030 | Studentloan | [studentloan_2020_03.md](studentloan_2020_03.md) |
| `studentloan_2021_07` | 907 | 2021–2031 | Studentloan | [studentloan_2021_07.md](studentloan_2021_07.md) |
| `studentloan_2022_05` | 920 | 2020–2032 | Studentloan | [studentloan_2022_05.md](studentloan_2022_05.md) |
| `studentloan_2023_05` | 892 | 2023–2033 | Studentloan | [studentloan_2023_05.md](studentloan_2023_05.md) |
| `studentloan_2024_06` | 800 | 2024–2034 | Studentloan | [studentloan_2024_06.md](studentloan_2024_06.md) |
| `tanf_2019_05` | 88 | 2019–2029 | Tanf | [tanf_2019_05.md](tanf_2019_05.md) |
| `tanf_2020_01` | 99 | 2020–2030 | Tanf | [tanf_2020_01.md](tanf_2020_01.md) |
| `tanf_2020_03` | 88 | 2020–2030 | Tanf | [tanf_2020_03.md](tanf_2020_03.md) |
| `tanf_2021_02` | 88 | 2021–2031 | Tanf | [tanf_2021_02.md](tanf_2021_02.md) |
| `tanf_2021_07` | 99 | 2021–2031 | Tanf | [tanf_2021_07.md](tanf_2021_07.md) |
| `tanf_2022_05` | 88 | 2022–2032 | Tanf | [tanf_2022_05.md](tanf_2022_05.md) |
| `tanf_2023_05` | 88 | 2023–2033 | Tanf | [tanf_2023_05.md](tanf_2023_05.md) |
| `tanf_2024_02` | 88 | 2024–2034 | Tanf | [tanf_2024_02.md](tanf_2024_02.md) |
| `tanf_2024_06` | 87 | 2024–2034 | Tanf | [tanf_2024_06.md](tanf_2024_06.md) |
| `tanf_2025_01` | 87 | 2025–2035 | Tanf | [tanf_2025_01.md](tanf_2025_01.md) |
| `tanf_2026_02` | 88 | 2026–2036 | Tanf | [tanf_2026_02.md](tanf_2026_02.md) |
| `tef_2024_06` | 195 | 2024–2034 | Tef | [tef_2024_06.md](tef_2024_06.md) |
| `tef_2025_01` | 195 | 2025–2035 | Tef | [tef_2025_01.md](tef_2025_01.md) |
| `toxic_exposures_fund_2024_02` | 195 | 2024–2034 | Toxic Exposures Fund | [toxic_exposures_fund_2024_02.md](toxic_exposures_fund_2024_02.md) |
| `trust_funds_2019_05` | 220 | 2019–2029 | Trust Funds | [trust_funds_2019_05.md](trust_funds_2019_05.md) |
| `trustfund_2020_01` | 204 | 2019–2030 | Trustfund | [trustfund_2020_01.md](trustfund_2020_01.md) |
| `trustfund_2020_03` | 204 | 2019–2030 | Trustfund | [trustfund_2020_03.md](trustfund_2020_03.md) |
| `trustfund_2021_07` | 176 | 2020–2031 | Trustfund | [trustfund_2021_07.md](trustfund_2021_07.md) |
| `trustfund_2022_05` | 234 | 2021–2032 | Trustfund | [trustfund_2022_05.md](trustfund_2022_05.md) |
| `trustfund_2023_05` | 232 | 2022–2033 | Trustfund | [trustfund_2023_05.md](trustfund_2023_05.md) |
| `trustfund_2024_02` | 232 | 2023–2034 | Trustfund | [trustfund_2024_02.md](trustfund_2024_02.md) |
| `trustfund_2024_06` | 232 | 2023–2034 | Trustfund | [trustfund_2024_06.md](trustfund_2024_06.md) |
| `trustfund_2025_01` | 253 | 2024–2035 | Trustfund | [trustfund_2025_01.md](trustfund_2025_01.md) |
| `unemployment_2019_05` | 99 | 2019–2029 | Unemployment | [unemployment_2019_05.md](unemployment_2019_05.md) |
| `unemployment_2020_01` | 99 | 2020–2030 | Unemployment | [unemployment_2020_01.md](unemployment_2020_01.md) |
| `unemployment_2020_03` | 99 | 2020–2030 | Unemployment | [unemployment_2020_03.md](unemployment_2020_03.md) |
| `unemployment_2021_02` | 209 | 2021–2031 | Unemployment | [unemployment_2021_02.md](unemployment_2021_02.md) |
| `unemployment_2021_07` | 209 | 2021–2031 | Unemployment | [unemployment_2021_07.md](unemployment_2021_07.md) |
| `unemployment_2022_05` | 209 | 2022–2032 | Unemployment | [unemployment_2022_05.md](unemployment_2022_05.md) |
| `unemployment_2023_05` | 143 | 2023–2033 | Unemployment | [unemployment_2023_05.md](unemployment_2023_05.md) |
| `unemployment_2024_02` | 143 | 2024–2034 | Unemployment | [unemployment_2024_02.md](unemployment_2024_02.md) |
| `unemployment_2024_06` | 143 | 2024–2034 | Unemployment | [unemployment_2024_06.md](unemployment_2024_06.md) |
| `unemployment_2025_01` | 99 | 2025–2035 | Unemployment | [unemployment_2025_01.md](unemployment_2025_01.md) |
| `unemployment_2026_02` | 99 | 2026–2036 | Unemployment | [unemployment_2026_02.md](unemployment_2026_02.md) |
| `usda_2024_02` | 384 | 2023–2034 | Usda | [usda_2024_02.md](usda_2024_02.md) |
| `usda_2025_01` | 276 | 2024–2035 | Usda | [usda_2025_01.md](usda_2025_01.md) |
| `veterans_2019_05` | 242 | 2019–2029 | Veterans | [veterans_2019_05.md](veterans_2019_05.md) |
| `veteransbenefit_2020_01` | 242 | 2020–2030 | Veteransbenefit | [veteransbenefit_2020_01.md](veteransbenefit_2020_01.md) |
| `veteransbenefit_2020_03` | 242 | 2020–2030 | Veteransbenefit | [veteransbenefit_2020_03.md](veteransbenefit_2020_03.md) |
| `veteransbenefit_2021_02` | 242 | 2021–2031 | Veteransbenefit. | [veteransbenefit_2021_02.md](veteransbenefit_2021_02.md) |
| `veteransbenefit_2022_05` | 132 | 2022–2032 | Veteransbenefit | [veteransbenefit_2022_05.md](veteransbenefit_2022_05.md) |
| `veteransbenefit_2023_05` | 132 | 2023–2033 | Veteransbenefit | [veteransbenefit_2023_05.md](veteransbenefit_2023_05.md) |
| `veteransbenefit_2024_02` | 132 | 2024–2034 | Veteransbenefit | [veteransbenefit_2024_02.md](veteransbenefit_2024_02.md) |
| `veteransbenefit_2025_01` | 176 | 2025–2035 | Veteransbenefit | [veteransbenefit_2025_01.md](veteransbenefit_2025_01.md) |
