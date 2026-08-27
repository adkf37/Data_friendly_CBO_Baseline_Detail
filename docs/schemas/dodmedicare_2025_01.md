# Schema: Dodmedicare 2025 01

- **Dataset:** `dodmedicare_2025_01`
- **Vintage:** 2025-01
- **Rows:** 121
- **Fiscal years covered:** 2025–2035

## Purpose

Tidy long-form CBO baseline data for the **DoD Medicare** program(s), extracted from CBO budget baseline workbooks published by the Congressional Budget Office. Each row represents one numeric source cell with explicit program, category hierarchy, period semantics, and cell-level provenance.

> **Aggregation caveat:** This dataset contains rows where `is_total = true`. These rows represent summary totals or subtotals drawn directly from the source worksheet. **Exclude `is_total = true` rows before summing across categories** to avoid double-counting.

## Provenance

| Field | Value |
|---|---|
| Source file(s) | `54946-2025-01-dodmedicare.xlsx` |
| Source sheet(s) | `DoD-MERHCF_0x-2024` |
| Unit(s) | Dollars per beneficiary, Millions of dollars, Thousands of people |

## Columns

| Column | Type | Description | Unit | Example | Notes |
|---|---|---|---|---|---|
| `program` | string | Canonical CBO program name keyed by the stable source identifier. | N/A | `DoD Medicare` | Stable across workbook vintages; use ``program_id`` as the machine key. |
| `category` | string | Leaf line-item label from the source worksheet. | N/A | `Estimated Outlays From the MERHCF` | Rows where ``is_total`` is ``true`` represent aggregated totals or subtotals and should be excluded from sum-based aggregations to avoid double-counting. |
| `fiscal_year` | integer or null | Annual federal fiscal year; blank for every other period type. | Year | `2025` | Historical actuals are retained. Consult ``period_type`` and the explicit period bounds before interpreting a row as annual fiscal-year data. |
| `value` | float | Parsed numeric value from the source cell. | See ``unit`` column | `12796.0` | Negative values indicate outflows or reductions. Values originally enclosed in parentheses (e.g. ``(123)``) are converted to negative floats. |
| `unit` | string | Unit of measure for ``value``, resolved from row/section labels and parse metadata. | N/A | `Millions of dollars` | Common values include 'Millions of dollars', 'Billions of dollars', and 'Thousands'. |
| `source_file` | string | Original CBO workbook filename from ``data/raw/``. | N/A | `54946-2025-01-dodmedicare.xlsx` | Use this column to trace any row back to its exact source workbook. |
| `source_sheet` | string | Worksheet name within the source workbook. | N/A | `DoD-MERHCF_0x-2024` | Combine with source file, row, and column for exact cell provenance. |
| `is_total` | boolean | ``true`` if the category label contains the word 'total' or 'subtotal', indicating an aggregated row. | N/A | `false` | **Always filter ``is_total = true`` rows out before computing sums or averages** across categories to avoid double-counting. Retain them for headline/summary views. |
| `program_id` | string | Stable numeric CBO identifier from the source filename. | N/A | `54946` | Preferred program join key across vintages. |
| `category_path` | string | Hierarchy-aware path from table/section headings to the leaf category. | N/A | `Department of Defense Medicare-Eligib...` | Use this field instead of ``category`` when labels repeat in different subprograms. |
| `period_type` | string | Period semantics for the observation. | N/A | `fiscal_year` | Values include fiscal_year, calendar_year, award_year, school_year, cumulative_fiscal_years, and unmapped. |
| `period_start_year` | integer or null | First year represented by the source period. | Year | `2025` | Equals period_end_year for annual rows and is blank when the source period is not identified. |
| `period_end_year` | integer or null | Last year represented by the source period. | Year | `2025` | For annual fiscal-year rows this equals ``fiscal_year``. |
| `period_label` | string | Normalized source period label such as 2025 or 2025-2029. | N/A | `2025` | Rows with unrecognized periods are labeled explicitly rather than assigned a guessed year. |
| `source_row` | integer | One-based worksheet row containing the numeric source value. | N/A | `13` | Together with ``source_column`` identifies the exact source cell. |
| `source_column` | integer | One-based worksheet column containing the numeric source value. | N/A | `4` | Together with ``source_row`` identifies the exact source cell. |

## Variable Notes

Superscript letter markers are read from the source workbook's actual Excel rich-text formatting. Each extracted note is attached to every affected `category_path`; a note on a parent heading therefore applies to its child rows. A source-only entry is retained when the annotated source label has no emitted row in the processed dataset.

| Affected category path | Marker | `variable_note` | Source label | Source cell |
|---|---|---|---|---|
| Department of Defense Medicare-Eligible Retiree Health Care Fund / Average Annual Beneficiaries (Thousands of people) / TRICARE for Lifea | `a` | TRICARE for Life (TFL) beneficiaries include all military retirees, survivors, and their dependents who are eligible for benefits from the MERHCF unless they are enrolled in USFHP. For those enrolled in Medicare Part B, benefits include the TFL Medicare wrap-around benefit, pharmacy benefits, and any care provided to those beneficiaries at military treatment facilities. TFL beneficiaries shown in this table also include those non-USFHP beneficiaries who are ineligible to use TFL because they are not enrolled in Medicare Part B but are still eligible for some benefits from the MERHCF, such as direct care at military treatment facilities. CBO estimates that about 90 percent of beneficiaries who are eligible for TFL use the benefit. | TRICARE for Lifea | `54946-2025-01-dodmedicare.xlsx` / `DoD-MERHCF_0x-2024` / R24C1 |
| Department of Defense Medicare-Eligible Retiree Health Care Fund / Average Annual Beneficiaries (Thousands of people) / USFHPb | `b` | The beneficiary projections for USFHP include CBO’s projection of Medicare-eligible beneficiaries enrolled in that program and exclude beneficiaries enrolled in USFHP who are not Medicare eligible. Costs for those beneficiaries are not paid from the MERHCF. The enrollment of Medicare-eligible beneficiaries in USFHP is declining over time because the National Defense Authorization Act for Fiscal Year 2012 limits future enrollment of Medicare-eligible beneficiaries to those enrolled as of the start of fiscal year 2013. | USFHPb | `54946-2025-01-dodmedicare.xlsx` / `DoD-MERHCF_0x-2024` / R25C1 |
| Department of Defense Medicare-Eligible Retiree Health Care Fund / TRICARE for Life / USFHPc | `c` | The costs per capita to the MERHCF for USFHP beneficiaries are greater than for TFL beneficiaries because USFHP is responsible for the full cost of care for its enrollees, whereas TFL pays only the portion of allowable charges not paid for by Medicare or another form of health insurance. | USFHPc | `54946-2025-01-dodmedicare.xlsx` / `DoD-MERHCF_0x-2024` / R39C1 |

## is_total Interpretation

The `is_total` column flags rows whose `category` label contains the word 'total' or 'subtotal'. These rows summarise multiple line items and must be treated carefully in downstream analysis:

- **Summary views:** Include `is_total = true` rows to display headline figures.
- **Detailed aggregations:** Exclude `is_total = true` rows to prevent double-counting when summing across categories.
- **Time-series analysis:** Either filter is consistent as long as it is applied uniformly across all fiscal years being compared.
