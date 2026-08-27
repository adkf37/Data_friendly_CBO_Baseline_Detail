# Schema: Premium TAX Credit 2024 07

- **Dataset:** `premium_tax_credit_2024_07`
- **Vintage:** 2024-07
- **Rows:** 33
- **Fiscal years covered:** 2024–2034

## Purpose

Tidy long-form CBO baseline data for the **Premium Tax Credit** program(s), extracted from CBO budget baseline workbooks published by the Congressional Budget Office. Each row represents one numeric source cell with explicit program, category hierarchy, period semantics, and cell-level provenance.

## Provenance

| Field | Value |
|---|---|
| Source file(s) | `60523-2024-07-premium-tax-credit.xlsx` |
| Source sheet(s) | `PTC_07-2024` |
| Unit(s) | Millions of people |

## Columns

| Column | Type | Description | Unit | Example | Notes |
|---|---|---|---|---|---|
| `program` | string | Canonical CBO program name keyed by the stable source identifier. | N/A | `Premium Tax Credit` | Stable across workbook vintages; use ``program_id`` as the machine key. |
| `category` | string | Leaf line-item label from the source worksheet. | N/A | `BHP Enrollmentb` | Rows where ``is_total`` is ``true`` represent aggregated totals or subtotals and should be excluded from sum-based aggregations to avoid double-counting. |
| `fiscal_year` | integer or null | Annual federal fiscal year; blank for every other period type. | Year | `2024` | Historical actuals are retained. Consult ``period_type`` and the explicit period bounds before interpreting a row as annual fiscal-year data. |
| `value` | float | Parsed numeric value from the source cell. | See ``unit`` column | `1.3` | Negative values indicate outflows or reductions. Values originally enclosed in parentheses (e.g. ``(123)``) are converted to negative floats. |
| `unit` | string | Unit of measure for ``value``, resolved from row/section labels and parse metadata. | N/A | `Millions of people` | Common values include 'Millions of dollars', 'Billions of dollars', and 'Thousands'. |
| `source_file` | string | Original CBO workbook filename from ``data/raw/``. | N/A | `60523-2024-07-premium-tax-credit.xlsx` | Use this column to trace any row back to its exact source workbook. |
| `source_sheet` | string | Worksheet name within the source workbook. | N/A | `PTC_07-2024` | Combine with source file, row, and column for exact cell provenance. |
| `is_total` | boolean | ``true`` if the category label contains the word 'total' or 'subtotal', indicating an aggregated row. | N/A | `false` | **Always filter ``is_total = true`` rows out before computing sums or averages** across categories to avoid double-counting. Retain them for headline/summary views. |
| `program_id` | string | Stable numeric CBO identifier from the source filename. | N/A | `60523` | Preferred program join key across vintages. |
| `category_path` | string | Hierarchy-aware path from table/section headings to the leaf category. | N/A | `The Premium Tax Credit and Related Sp...` | Use this field instead of ``category`` when labels repeat in different subprograms. |
| `period_type` | string | Period semantics for the observation. | N/A | `fiscal_year` | Values include fiscal_year, calendar_year, award_year, school_year, cumulative_fiscal_years, and unmapped. |
| `period_start_year` | integer or null | First year represented by the source period. | Year | `2024` | Equals period_end_year for annual rows and is blank when the source period is not identified. |
| `period_end_year` | integer or null | Last year represented by the source period. | Year | `2024` | For annual fiscal-year rows this equals ``fiscal_year``. |
| `period_label` | string | Normalized source period label such as 2025 or 2025-2029. | N/A | `2024` | Rows with unrecognized periods are labeled explicitly rather than assigned a guessed year. |
| `source_row` | integer | One-based worksheet row containing the numeric source value. | N/A | `30` | Together with ``source_column`` identifies the exact source cell. |
| `source_column` | integer | One-based worksheet column containing the numeric source value. | N/A | `4` | Together with ``source_row`` identifies the exact source cell. |

## Variable Notes

Superscript letter markers are read from the source workbook's actual Excel rich-text formatting. Each extracted note is attached to every affected `category_path`; a note on a parent heading therefore applies to its child rows. A source-only entry is retained when the annotated source label has no emitted row in the processed dataset.

| Affected category path | Marker | `variable_note` | Source label | Source cell |
|---|---|---|---|---|
| *Source label is not represented in processed rows.* | `a` | The risk-adjustment program is intended to stabilize premiums in the nongroup and small-group markets, without affecting the federal budget. The federal government collects fees from insurers with enrollees who are relatively more healthy and makes roughly offsetting payments to insurers with enrollees who are relatively less healthy. | Collections for risk adjustmenta | `60523-2024-07-premium-tax-credit.xlsx` / `PTC_07-2024` / R17C2 |
| *Source label is not represented in processed rows.* | `a` | The risk-adjustment program is intended to stabilize premiums in the nongroup and small-group markets, without affecting the federal budget. The federal government collects fees from insurers with enrollees who are relatively more healthy and makes roughly offsetting payments to insurers with enrollees who are relatively less healthy. | Payments for risk adjustmenta | `60523-2024-07-premium-tax-credit.xlsx` / `PTC_07-2024` / R18C2 |
| The Premium Tax Credit and Related Spending / Marketplace Enrollment / BHP Enrollmentb | `b` | Only Minnesota and Oregon currently operate a BHP. Estimates include enrollment in New York’s Essential Plan, which is funded through a section 1332 waiver and mirrors the BHP; enrollees with household income up to 250 percent of the federal poverty level are eligible. | BHP Enrollmentb | `60523-2024-07-premium-tax-credit.xlsx` / `PTC_07-2024` / R30C1 |

## is_total Interpretation

The `is_total` column flags rows whose `category` label contains the word 'total' or 'subtotal'. These rows summarise multiple line items and must be treated carefully in downstream analysis:

- **Summary views:** Include `is_total = true` rows to display headline figures.
- **Detailed aggregations:** Exclude `is_total = true` rows to prevent double-counting when summing across categories.
- **Time-series analysis:** Either filter is consistent as long as it is applied uniformly across all fiscal years being compared.
