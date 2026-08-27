# Schema: Medicaid 2024 06

- **Dataset:** `medicaid_2024_06`
- **Vintage:** 2024-06
- **Rows:** 308
- **Fiscal years covered:** 2024–2034

## Purpose

Tidy long-form CBO baseline data for the **Medicaid** program(s), extracted from CBO budget baseline workbooks published by the Congressional Budget Office. Each row represents one numeric source cell with explicit program, category hierarchy, period semantics, and cell-level provenance.

> **Aggregation caveat:** This dataset contains rows where `is_total = true`. These rows represent summary totals or subtotals drawn directly from the source worksheet. **Exclude `is_total = true` rows before summing across categories** to avoid double-counting.

## Provenance

| Field | Value |
|---|---|
| Source file(s) | `51301-2024-06-medicaid.xlsx` |
| Source sheet(s) | `Medicaid_06-2024-rev` |
| Unit(s) | Billions of dollars, Dollars per enrollee, Millions of people |

## Columns

| Column | Type | Description | Unit | Example | Notes |
|---|---|---|---|---|---|
| `program` | string | Canonical CBO program name keyed by the stable source identifier. | N/A | `Medicaid` | Stable across workbook vintages; use ``program_id`` as the machine key. |
| `category` | string | Leaf line-item label from the source worksheet. | N/A | `Estimated Outlaysa` | Rows where ``is_total`` is ``true`` represent aggregated totals or subtotals and should be excluded from sum-based aggregations to avoid double-counting. |
| `fiscal_year` | integer or null | Annual federal fiscal year; blank for every other period type. | Year | `2024` | Historical actuals are retained. Consult ``period_type`` and the explicit period bounds before interpreting a row as annual fiscal-year data. |
| `value` | float | Parsed numeric value from the source cell. | See ``unit`` column | `607.0` | Negative values indicate outflows or reductions. Values originally enclosed in parentheses (e.g. ``(123)``) are converted to negative floats. |
| `unit` | string | Unit of measure for ``value``, resolved from row/section labels and parse metadata. | N/A | `Billions of dollars` | Common values include 'Millions of dollars', 'Billions of dollars', and 'Thousands'. |
| `source_file` | string | Original CBO workbook filename from ``data/raw/``. | N/A | `51301-2024-06-medicaid.xlsx` | Use this column to trace any row back to its exact source workbook. |
| `source_sheet` | string | Worksheet name within the source workbook. | N/A | `Medicaid_06-2024-rev` | Combine with source file, row, and column for exact cell provenance. |
| `is_total` | boolean | ``true`` if the category label contains the word 'total' or 'subtotal', indicating an aggregated row. | N/A | `false` | **Always filter ``is_total = true`` rows out before computing sums or averages** across categories to avoid double-counting. Retain them for headline/summary views. |
| `program_id` | string | Stable numeric CBO identifier from the source filename. | N/A | `51301` | Preferred program join key across vintages. |
| `category_path` | string | Hierarchy-aware path from table/section headings to the leaf category. | N/A | `Actual, / BUDGET INFORMATION / Estima...` | Use this field instead of ``category`` when labels repeat in different subprograms. |
| `period_type` | string | Period semantics for the observation. | N/A | `fiscal_year` | Values include fiscal_year, calendar_year, award_year, school_year, cumulative_fiscal_years, and unmapped. |
| `period_start_year` | integer or null | First year represented by the source period. | Year | `2024` | Equals period_end_year for annual rows and is blank when the source period is not identified. |
| `period_end_year` | integer or null | Last year represented by the source period. | Year | `2024` | For annual fiscal-year rows this equals ``fiscal_year``. |
| `period_label` | string | Normalized source period label such as 2025 or 2025-2029. | N/A | `2024` | Rows with unrecognized periods are labeled explicitly rather than assigned a guessed year. |
| `source_row` | integer | One-based worksheet row containing the numeric source value. | N/A | `14` | Together with ``source_column`` identifies the exact source cell. |
| `source_column` | integer | One-based worksheet column containing the numeric source value. | N/A | `5` | Together with ``source_row`` identifies the exact source cell. |

## Variable Notes

Superscript letter markers are read from the source workbook's actual Excel rich-text formatting. Each extracted note is attached to every affected `category_path`; a note on a parent heading therefore applies to its child rows. A source-only entry is retained when the annotated source label has no emitted row in the processed dataset.

| Affected category path | Marker | `variable_note` | Source label | Source cell |
|---|---|---|---|---|
| Actual, / BUDGET INFORMATION / Estimated Outlaysa | `a` | On average, before fiscal year 2014, federal Medicaid payments represented approximately 57 percent of total Medicaid payments. The ACA, which expanded Medicaid coverage starting in 2014, provides enhanced federal matching rates for services to those made eligible by that act, leading to a federal share for all Medicaid payments of about 65 percent, on average. In addition, for the duration of the coronavirus public health emergency, the Families First Coronavirus Relief Act increased matching rates by 6.2 percentage points for services provided to people who were not made eligible by the ACA. The Consolidated Appropriations Act of 2023 terminated that provision, establishing a gradual phasedown of the increased matching rates beginning in April 2023 through the end of calendar year 2023. | Estimated Outlaysa | `51301-2024-06-medicaid.xlsx` / `Medicaid_06-2024-rev` / R14C1 |
| Actual, / Average Monthly Enrollment by Eligibility Category (Millions of people)b / Adults—Made eligible by the ACA | `b` | These figures represent the number of beneficiaries with full and partial benefits who are enrolled on an average monthly basis. The total number of people enrolled in Medicaid for any length of time during the fiscal year is shown in the memorandum line. | Average Monthly Enrollment by Eligibility Category (Millions of people)b | `51301-2024-06-medicaid.xlsx` / `Medicaid_06-2024-rev` / R43C1 |
| Actual, / Average Monthly Enrollment by Eligibility Category (Millions of people)b / Adults—Traditional eligibility categories | `b` | These figures represent the number of beneficiaries with full and partial benefits who are enrolled on an average monthly basis. The total number of people enrolled in Medicaid for any length of time during the fiscal year is shown in the memorandum line. | Average Monthly Enrollment by Eligibility Category (Millions of people)b | `51301-2024-06-medicaid.xlsx` / `Medicaid_06-2024-rev` / R43C1 |
| Actual, / Average Monthly Enrollment by Eligibility Category (Millions of people)b / Aged | `b` | These figures represent the number of beneficiaries with full and partial benefits who are enrolled on an average monthly basis. The total number of people enrolled in Medicaid for any length of time during the fiscal year is shown in the memorandum line. | Average Monthly Enrollment by Eligibility Category (Millions of people)b | `51301-2024-06-medicaid.xlsx` / `Medicaid_06-2024-rev` / R43C1 |
| Actual, / Average Monthly Enrollment by Eligibility Category (Millions of people)b / Blind and Disabled | `b` | These figures represent the number of beneficiaries with full and partial benefits who are enrolled on an average monthly basis. The total number of people enrolled in Medicaid for any length of time during the fiscal year is shown in the memorandum line. | Average Monthly Enrollment by Eligibility Category (Millions of people)b | `51301-2024-06-medicaid.xlsx` / `Medicaid_06-2024-rev` / R43C1 |
| Actual, / Average Monthly Enrollment by Eligibility Category (Millions of people)b / Children | `b` | These figures represent the number of beneficiaries with full and partial benefits who are enrolled on an average monthly basis. The total number of people enrolled in Medicaid for any length of time during the fiscal year is shown in the memorandum line. | Average Monthly Enrollment by Eligibility Category (Millions of people)b | `51301-2024-06-medicaid.xlsx` / `Medicaid_06-2024-rev` / R43C1 |
| Actual, / Average Monthly Enrollment by Eligibility Category (Millions of people)b / Total | `b` | These figures represent the number of beneficiaries with full and partial benefits who are enrolled on an average monthly basis. The total number of people enrolled in Medicaid for any length of time during the fiscal year is shown in the memorandum line. | Average Monthly Enrollment by Eligibility Category (Millions of people)b | `51301-2024-06-medicaid.xlsx` / `Medicaid_06-2024-rev` / R43C1 |
| Actual, / Average Federal Spending on Benefit Payments per Enrollee (Dollars)c / Adults–Made eligible by the ACA | `c` | These figures are based on the annual cost for enrollees who receive any Medicaid benefit—including those who receive only partial Medicaid benefits, such as family planning services or assistance with Medicare cost sharing and premiums. | Average Federal Spending on Benefit Payments per Enrollee (Dollars)c | `51301-2024-06-medicaid.xlsx` / `Medicaid_06-2024-rev` / R57C1 |
| Actual, / Average Federal Spending on Benefit Payments per Enrollee (Dollars)c / Adults–Traditional eligibility categories | `c` | These figures are based on the annual cost for enrollees who receive any Medicaid benefit—including those who receive only partial Medicaid benefits, such as family planning services or assistance with Medicare cost sharing and premiums. | Average Federal Spending on Benefit Payments per Enrollee (Dollars)c | `51301-2024-06-medicaid.xlsx` / `Medicaid_06-2024-rev` / R57C1 |
| Actual, / Average Federal Spending on Benefit Payments per Enrollee (Dollars)c / Aged | `c` | These figures are based on the annual cost for enrollees who receive any Medicaid benefit—including those who receive only partial Medicaid benefits, such as family planning services or assistance with Medicare cost sharing and premiums. | Average Federal Spending on Benefit Payments per Enrollee (Dollars)c | `51301-2024-06-medicaid.xlsx` / `Medicaid_06-2024-rev` / R57C1 |
| Actual, / Average Federal Spending on Benefit Payments per Enrollee (Dollars)c / Blind and Disabled | `c` | These figures are based on the annual cost for enrollees who receive any Medicaid benefit—including those who receive only partial Medicaid benefits, such as family planning services or assistance with Medicare cost sharing and premiums. | Average Federal Spending on Benefit Payments per Enrollee (Dollars)c | `51301-2024-06-medicaid.xlsx` / `Medicaid_06-2024-rev` / R57C1 |
| Actual, / Average Federal Spending on Benefit Payments per Enrollee (Dollars)c / Children | `c` | These figures are based on the annual cost for enrollees who receive any Medicaid benefit—including those who receive only partial Medicaid benefits, such as family planning services or assistance with Medicare cost sharing and premiums. | Average Federal Spending on Benefit Payments per Enrollee (Dollars)c | `51301-2024-06-medicaid.xlsx` / `Medicaid_06-2024-rev` / R57C1 |

## is_total Interpretation

The `is_total` column flags rows whose `category` label contains the word 'total' or 'subtotal'. These rows summarise multiple line items and must be treated carefully in downstream analysis:

- **Summary views:** Include `is_total = true` rows to display headline figures.
- **Detailed aggregations:** Exclude `is_total = true` rows to prevent double-counting when summing across categories.
- **Time-series analysis:** Either filter is consistent as long as it is applied uniformly across all fiscal years being compared.
