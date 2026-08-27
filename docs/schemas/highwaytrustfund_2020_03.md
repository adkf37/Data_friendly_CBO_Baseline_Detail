# Schema: Highwaytrustfund 2020 03

- **Dataset:** `highwaytrustfund_2020_03`
- **Vintage:** 2020-03
- **Rows:** 103
- **Fiscal years covered:** 2019–2030

## Purpose

Tidy long-form CBO baseline data for the **Highway Trust Fund** program(s), extracted from CBO budget baseline workbooks published by the Congressional Budget Office. Each row represents one numeric source cell with explicit program, category hierarchy, period semantics, and cell-level provenance.

## Provenance

| Field | Value |
|---|---|
| Source file(s) | `51300-2020-03-highwaytrustfund.xlsx` |
| Source sheet(s) | `Highway Trust Fund` |
| Unit(s) | Millions of dollars |

## Columns

| Column | Type | Description | Unit | Example | Notes |
|---|---|---|---|---|---|
| `program` | string | Canonical CBO program name keyed by the stable source identifier. | N/A | `Highway Trust Fund` | Stable across workbook vintages; use ``program_id`` as the machine key. |
| `category` | string | Leaf line-item label from the source worksheet. | N/A | `Start-of-Year Balance` | Rows where ``is_total`` is ``true`` represent aggregated totals or subtotals and should be excluded from sum-based aggregations to avoid double-counting. |
| `fiscal_year` | integer or null | Annual federal fiscal year; blank for every other period type. | Year | `2019` | Historical actuals are retained. Consult ``period_type`` and the explicit period bounds before interpreting a row as annual fiscal-year data. |
| `value` | float | Parsed numeric value from the source cell. | See ``unit`` column | `32605.0` | Negative values indicate outflows or reductions. Values originally enclosed in parentheses (e.g. ``(123)``) are converted to negative floats. |
| `unit` | string | Unit of measure for ``value``, resolved from row/section labels and parse metadata. | N/A | `Millions of dollars` | Common values include 'Millions of dollars', 'Billions of dollars', and 'Thousands'. |
| `source_file` | string | Original CBO workbook filename from ``data/raw/``. | N/A | `51300-2020-03-highwaytrustfund.xlsx` | Use this column to trace any row back to its exact source workbook. |
| `source_sheet` | string | Worksheet name within the source workbook. | N/A | `Highway Trust Fund` | Combine with source file, row, and column for exact cell provenance. |
| `is_total` | boolean | ``true`` if the category label contains the word 'total' or 'subtotal', indicating an aggregated row. | N/A | `false` | **Always filter ``is_total = true`` rows out before computing sums or averages** across categories to avoid double-counting. Retain them for headline/summary views. |
| `program_id` | string | Stable numeric CBO identifier from the source filename. | N/A | `51300` | Preferred program join key across vintages. |
| `category_path` | string | Hierarchy-aware path from table/section headings to the leaf category. | N/A | `Start-of-Year Balance` | Use this field instead of ``category`` when labels repeat in different subprograms. |
| `period_type` | string | Period semantics for the observation. | N/A | `fiscal_year` | Values include fiscal_year, calendar_year, award_year, school_year, cumulative_fiscal_years, and unmapped. |
| `period_start_year` | integer or null | First year represented by the source period. | Year | `2019` | Equals period_end_year for annual rows and is blank when the source period is not identified. |
| `period_end_year` | integer or null | Last year represented by the source period. | Year | `2019` | For annual fiscal-year rows this equals ``fiscal_year``. |
| `period_label` | string | Normalized source period label such as 2025 or 2025-2029. | N/A | `2019` | Rows with unrecognized periods are labeled explicitly rather than assigned a guessed year. |
| `source_row` | integer | One-based worksheet row containing the numeric source value. | N/A | `8` | Together with ``source_column`` identifies the exact source cell. |
| `source_column` | integer | One-based worksheet column containing the numeric source value. | N/A | `5` | Together with ``source_row`` identifies the exact source cell. |

## Variable Notes

Superscript letter markers are read from the source workbook's actual Excel rich-text formatting. Each extracted note is attached to every affected `category_path`; a note on a parent heading therefore applies to its child rows. A source-only entry is retained when the annotated source label has no emitted row in the processed dataset.

| Affected category path | Marker | `variable_note` | Source label | Source cell |
|---|---|---|---|---|
| Flexed Balancesb | `b` | Flexed balances are amounts transferred from the highway account to the transit account. | Flexed Balancesb | `51300-2020-03-highwaytrustfund.xlsx` / `Highway Trust Fund` / R9C1 |
| Revenues and Interestc | `c` | Some of the taxes that are credited to the Highway Trust Fund are scheduled to expire on September 30, 2022, including the taxes on tires and all but 4.3 cents of the federal tax on motor fuels. However, under the rules governing baseline projections, these estimates reflect the assumption that all of the expiring taxes credited to the fund will continue to be collected after fiscal year 2022. | Revenues and Interestc | `51300-2020-03-highwaytrustfund.xlsx` / `Highway Trust Fund` / R10C1 |
| Flexed Balancesb | `b` | Flexed balances are amounts transferred from the highway account to the transit account. | Flexed Balancesb | `51300-2020-03-highwaytrustfund.xlsx` / `Highway Trust Fund` / R16C1 |
| Revenues and Interestc | `c` | Some of the taxes that are credited to the Highway Trust Fund are scheduled to expire on September 30, 2022, including the taxes on tires and all but 4.3 cents of the federal tax on motor fuels. However, under the rules governing baseline projections, these estimates reflect the assumption that all of the expiring taxes credited to the fund will continue to be collected after fiscal year 2022. | Revenues and Interestc | `51300-2020-03-highwaytrustfund.xlsx` / `Highway Trust Fund` / R17C1 |
| Cumulative Shortfalla / Highway Account | `a` | Under current law, the Highway Trust Fund cannot incur negative balances. However, following the rules governing baseline projections in the Balanced Budget and Emergency Deficit Control Act of 1985, CBO's baseline for surface transportation spending reflects the assumption that obligations presented to the Highway Trust Fund will be paid in full. The memorandum to this table shows the cumulative shortfall of fund balances, assuming spending amounts consistent with CBO's March 2020 baseline. Following the rules for baseline construction, those amounts are estimated by adjusting the obligation limitations enacted under P.L. 116-94, the Further Consolidated Appropriations Act, 2020, by projected inflation. | Cumulative Shortfalla | `51300-2020-03-highwaytrustfund.xlsx` / `Highway Trust Fund` / R22C1 |
| Cumulative Shortfalla / Transit Account | `a` | Under current law, the Highway Trust Fund cannot incur negative balances. However, following the rules governing baseline projections in the Balanced Budget and Emergency Deficit Control Act of 1985, CBO's baseline for surface transportation spending reflects the assumption that obligations presented to the Highway Trust Fund will be paid in full. The memorandum to this table shows the cumulative shortfall of fund balances, assuming spending amounts consistent with CBO's March 2020 baseline. Following the rules for baseline construction, those amounts are estimated by adjusting the obligation limitations enacted under P.L. 116-94, the Further Consolidated Appropriations Act, 2020, by projected inflation. | Cumulative Shortfalla | `51300-2020-03-highwaytrustfund.xlsx` / `Highway Trust Fund` / R22C1 |

## is_total Interpretation

The `is_total` column flags rows whose `category` label contains the word 'total' or 'subtotal'. These rows summarise multiple line items and must be treated carefully in downstream analysis:

- **Summary views:** Include `is_total = true` rows to display headline figures.
- **Detailed aggregations:** Exclude `is_total = true` rows to prevent double-counting when summing across categories.
- **Time-series analysis:** Either filter is consistent as long as it is applied uniformly across all fiscal years being compared.
