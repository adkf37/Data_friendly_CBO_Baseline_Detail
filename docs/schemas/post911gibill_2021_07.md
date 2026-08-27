# Schema: Post911Gibill 2021 07

- **Dataset:** `post911gibill_2021_07`
- **Vintage:** 2021-07
- **Rows:** 55
- **Fiscal years covered:** 2021–2031

## Purpose

Tidy long-form CBO baseline data for the **Post-9/11 GI Bill** program(s), extracted from CBO budget baseline workbooks published by the Congressional Budget Office. Each row represents one numeric source cell with explicit program, category hierarchy, period semantics, and cell-level provenance.

> **Aggregation caveat:** This dataset contains rows where `is_total = true`. These rows represent summary totals or subtotals drawn directly from the source worksheet. **Exclude `is_total = true` rows before summing across categories** to avoid double-counting.

## Provenance

| Field | Value |
|---|---|
| Source file(s) | `53726-2021-07-post911gibill.xlsx` |
| Source sheet(s) | `Post911_` |
| Unit(s) | Dollars per beneficiary, Millions of dollars, Thousands of people |

## Columns

| Column | Type | Description | Unit | Example | Notes |
|---|---|---|---|---|---|
| `program` | string | Canonical CBO program name keyed by the stable source identifier. | N/A | `Post-9/11 GI Bill` | Stable across workbook vintages; use ``program_id`` as the machine key. |
| `category` | string | Leaf line-item label from the source worksheet. | N/A | `Total Payments` | Rows where ``is_total`` is ``true`` represent aggregated totals or subtotals and should be excluded from sum-based aggregations to avoid double-counting. |
| `fiscal_year` | integer or null | Annual federal fiscal year; blank for every other period type. | Year | `2021` | Historical actuals are retained. Consult ``period_type`` and the explicit period bounds before interpreting a row as annual fiscal-year data. |
| `value` | float | Parsed numeric value from the source cell. | See ``unit`` column | `9077.0` | Negative values indicate outflows or reductions. Values originally enclosed in parentheses (e.g. ``(123)``) are converted to negative floats. |
| `unit` | string | Unit of measure for ``value``, resolved from row/section labels and parse metadata. | N/A | `Millions of dollars` | Common values include 'Millions of dollars', 'Billions of dollars', and 'Thousands'. |
| `source_file` | string | Original CBO workbook filename from ``data/raw/``. | N/A | `53726-2021-07-post911gibill.xlsx` | Use this column to trace any row back to its exact source workbook. |
| `source_sheet` | string | Worksheet name within the source workbook. | N/A | `Post911_` | Combine with source file, row, and column for exact cell provenance. |
| `is_total` | boolean | ``true`` if the category label contains the word 'total' or 'subtotal', indicating an aggregated row. | N/A | `true` | **Always filter ``is_total = true`` rows out before computing sums or averages** across categories to avoid double-counting. Retain them for headline/summary views. |
| `program_id` | string | Stable numeric CBO identifier from the source filename. | N/A | `53726` | Preferred program join key across vintages. |
| `category_path` | string | Hierarchy-aware path from table/section headings to the leaf category. | N/A | `Post-9/11 GI Bill Benefits / Outlays ...` | Use this field instead of ``category`` when labels repeat in different subprograms. |
| `period_type` | string | Period semantics for the observation. | N/A | `fiscal_year` | Values include fiscal_year, calendar_year, award_year, school_year, cumulative_fiscal_years, and unmapped. |
| `period_start_year` | integer or null | First year represented by the source period. | Year | `2021` | Equals period_end_year for annual rows and is blank when the source period is not identified. |
| `period_end_year` | integer or null | Last year represented by the source period. | Year | `2021` | For annual fiscal-year rows this equals ``fiscal_year``. |
| `period_label` | string | Normalized source period label such as 2025 or 2025-2029. | N/A | `2021` | Rows with unrecognized periods are labeled explicitly rather than assigned a guessed year. |
| `source_row` | integer | One-based worksheet row containing the numeric source value. | N/A | `14` | Together with ``source_column`` identifies the exact source cell. |
| `source_column` | integer | One-based worksheet column containing the numeric source value. | N/A | `5` | Together with ``source_row`` identifies the exact source cell. |

## Variable Notes

Superscript letter markers are read from the source workbook's actual Excel rich-text formatting. Each extracted note is attached to every affected `category_path`; a note on a parent heading therefore applies to its child rows. A source-only entry is retained when the annotated source label has no emitted row in the processed dataset.

| Affected category path | Marker | `variable_note` | Source label | Source cell |
|---|---|---|---|---|
| Post-9/11 GI Bill Benefits / Outlays in millions of dollars, by fiscal year / Adjustment for Timing Shiftsa | `a` | VA makes certain payments under the Post-9/11 GI Bill (housing allowances and supplementary benefits) to beneficiaries on the first day of the month. If the first day of the month occurs on a weekend or holiday, VA will make the payments on the preceding business day. When this occurs in October (the beginning of the fiscal year), the payment is made at the end of September (in the preceding fiscal year). This results in shifting the October payments in fiscal years 2023, 2024, and 2029 backward into fiscal years 2022, 2023, and 2028, respectively. | Adjustment for Timing Shiftsa | `53726-2021-07-post911gibill.xlsx` / `Post911_` / R15C2 |

## is_total Interpretation

The `is_total` column flags rows whose `category` label contains the word 'total' or 'subtotal'. These rows summarise multiple line items and must be treated carefully in downstream analysis:

- **Summary views:** Include `is_total = true` rows to display headline figures.
- **Detailed aggregations:** Exclude `is_total = true` rows to prevent double-counting when summing across categories.
- **Time-series analysis:** Either filter is consistent as long as it is applied uniformly across all fiscal years being compared.
