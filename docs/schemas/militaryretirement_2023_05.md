# Schema: Militaryretirement 2023 05

- **Dataset:** `militaryretirement_2023_05`
- **Vintage:** 2023-05
- **Rows:** 96
- **Fiscal years covered:** 2023–2033

## Purpose

Tidy long-form CBO baseline data for the **Military Retirement** program(s), extracted from CBO budget baseline workbooks published by the Congressional Budget Office. Each row represents one numeric source cell with explicit program, category hierarchy, period semantics, and cell-level provenance.

## Provenance

| Field | Value |
|---|---|
| Source file(s) | `51303-2023-05-militaryretirement.xlsx` |
| Source sheet(s) | `Mil Retirement_05-2023` |
| Unit(s) | Billions of dollars, Dollars per participant, Thousands of people |

## Columns

| Column | Type | Description | Unit | Example | Notes |
|---|---|---|---|---|---|
| `program` | string | Canonical CBO program name keyed by the stable source identifier. | N/A | `Military Retirement` | Stable across workbook vintages; use ``program_id`` as the machine key. |
| `category` | string | Leaf line-item label from the source worksheet. | N/A | `Budget Authority` | Rows where ``is_total`` is ``true`` represent aggregated totals or subtotals and should be excluded from sum-based aggregations to avoid double-counting. |
| `fiscal_year` | integer or null | Annual federal fiscal year; blank for every other period type. | Year | `2023` | Historical actuals are retained. Consult ``period_type`` and the explicit period bounds before interpreting a row as annual fiscal-year data. |
| `value` | float | Parsed numeric value from the source cell. | See ``unit`` column | `74400.0` | Negative values indicate outflows or reductions. Values originally enclosed in parentheses (e.g. ``(123)``) are converted to negative floats. |
| `unit` | string | Unit of measure for ``value``, resolved from row/section labels and parse metadata. | N/A | `Billions of dollars` | Common values include 'Millions of dollars', 'Billions of dollars', and 'Thousands'. |
| `source_file` | string | Original CBO workbook filename from ``data/raw/``. | N/A | `51303-2023-05-militaryretirement.xlsx` | Use this column to trace any row back to its exact source workbook. |
| `source_sheet` | string | Worksheet name within the source workbook. | N/A | `Mil Retirement_05-2023` | Combine with source file, row, and column for exact cell provenance. |
| `is_total` | boolean | ``true`` if the category label contains the word 'total' or 'subtotal', indicating an aggregated row. | N/A | `false` | **Always filter ``is_total = true`` rows out before computing sums or averages** across categories to avoid double-counting. Retain them for headline/summary views. |
| `program_id` | string | Stable numeric CBO identifier from the source filename. | N/A | `51303` | Preferred program join key across vintages. |
| `category_path` | string | Hierarchy-aware path from table/section headings to the leaf category. | N/A | `Military Retirement / BUDGET INFORMAT...` | Use this field instead of ``category`` when labels repeat in different subprograms. |
| `period_type` | string | Period semantics for the observation. | N/A | `fiscal_year` | Values include fiscal_year, calendar_year, award_year, school_year, cumulative_fiscal_years, and unmapped. |
| `period_start_year` | integer or null | First year represented by the source period. | Year | `2023` | Equals period_end_year for annual rows and is blank when the source period is not identified. |
| `period_end_year` | integer or null | Last year represented by the source period. | Year | `2023` | For annual fiscal-year rows this equals ``fiscal_year``. |
| `period_label` | string | Normalized source period label such as 2025 or 2025-2029. | N/A | `2023` | Rows with unrecognized periods are labeled explicitly rather than assigned a guessed year. |
| `source_row` | integer | One-based worksheet row containing the numeric source value. | N/A | `13` | Together with ``source_column`` identifies the exact source cell. |
| `source_column` | integer | One-based worksheet column containing the numeric source value. | N/A | `4` | Together with ``source_row`` identifies the exact source cell. |

## is_total Interpretation

The `is_total` column flags rows whose `category` label contains the word 'total' or 'subtotal'. These rows summarise multiple line items and must be treated carefully in downstream analysis:

- **Summary views:** Include `is_total = true` rows to display headline figures.
- **Detailed aggregations:** Exclude `is_total = true` rows to prevent double-counting when summing across categories.
- **Time-series analysis:** Either filter is consistent as long as it is applied uniformly across all fiscal years being compared.
