# Schema: Railroadretirement 2026 02

- **Dataset:** `railroadretirement_2026_02`
- **Vintage:** 2026-02
- **Rows:** 66
- **Fiscal years covered:** 2026–2036

## Purpose

Tidy long-form CBO baseline data for the **Railroad Retirement** program(s), extracted from CBO budget baseline workbooks published by the Congressional Budget Office. Each row represents one numeric source cell with explicit program, category hierarchy, period semantics, and cell-level provenance.

> **Aggregation caveat:** This dataset contains rows where `is_total = true`. These rows represent summary totals or subtotals drawn directly from the source worksheet. **Exclude `is_total = true` rows before summing across categories** to avoid double-counting.

## Provenance

| Field | Value |
|---|---|
| Source file(s) | `51306-2026-02-railroadretirement.xlsx` |
| Source sheet(s) | `RailroadRetirement_02-2026` |
| Unit(s) | Millions of dollars, Number of beneficiaries |

## Columns

| Column | Type | Description | Unit | Example | Notes |
|---|---|---|---|---|---|
| `program` | string | Canonical CBO program name keyed by the stable source identifier. | N/A | `Railroad Retirement` | Stable across workbook vintages; use ``program_id`` as the machine key. |
| `category` | string | Leaf line-item label from the source worksheet. | N/A | `Tier Ia` | Rows where ``is_total`` is ``true`` represent aggregated totals or subtotals and should be excluded from sum-based aggregations to avoid double-counting. |
| `fiscal_year` | integer or null | Annual federal fiscal year; blank for every other period type. | Year | `2026` | Historical actuals are retained. Consult ``period_type`` and the explicit period bounds before interpreting a row as annual fiscal-year data. |
| `value` | float | Parsed numeric value from the source cell. | See ``unit`` column | `8870.0` | Negative values indicate outflows or reductions. Values originally enclosed in parentheses (e.g. ``(123)``) are converted to negative floats. |
| `unit` | string | Unit of measure for ``value``, resolved from row/section labels and parse metadata. | N/A | `Millions of dollars` | Common values include 'Millions of dollars', 'Billions of dollars', and 'Thousands'. |
| `source_file` | string | Original CBO workbook filename from ``data/raw/``. | N/A | `51306-2026-02-railroadretirement.xlsx` | Use this column to trace any row back to its exact source workbook. |
| `source_sheet` | string | Worksheet name within the source workbook. | N/A | `RailroadRetirement_02-2026` | Combine with source file, row, and column for exact cell provenance. |
| `is_total` | boolean | ``true`` if the category label contains the word 'total' or 'subtotal', indicating an aggregated row. | N/A | `false` | **Always filter ``is_total = true`` rows out before computing sums or averages** across categories to avoid double-counting. Retain them for headline/summary views. |
| `program_id` | string | Stable numeric CBO identifier from the source filename. | N/A | `51306` | Preferred program join key across vintages. |
| `category_path` | string | Hierarchy-aware path from table/section headings to the leaf category. | N/A | `Railroad Retirement / BUDGET INFORMAT...` | Use this field instead of ``category`` when labels repeat in different subprograms. |
| `period_type` | string | Period semantics for the observation. | N/A | `fiscal_year` | Values include fiscal_year, calendar_year, award_year, school_year, cumulative_fiscal_years, and unmapped. |
| `period_start_year` | integer or null | First year represented by the source period. | Year | `2026` | Equals period_end_year for annual rows and is blank when the source period is not identified. |
| `period_end_year` | integer or null | Last year represented by the source period. | Year | `2026` | For annual fiscal-year rows this equals ``fiscal_year``. |
| `period_label` | string | Normalized source period label such as 2025 or 2025-2029. | N/A | `2026` | Rows with unrecognized periods are labeled explicitly rather than assigned a guessed year. |
| `source_row` | integer | One-based worksheet row containing the numeric source value. | N/A | `13` | Together with ``source_column`` identifies the exact source cell. |
| `source_column` | integer | One-based worksheet column containing the numeric source value. | N/A | `4` | Together with ``source_row`` identifies the exact source cell. |

## Variable Notes

Superscript letter markers are read from the source workbook's actual Excel rich-text formatting. Each extracted note is attached to every affected `category_path`; a note on a parent heading therefore applies to its child rows. A source-only entry is retained when the annotated source label has no emitted row in the processed dataset.

| Affected category path | Marker | `variable_note` | Source label | Source cell |
|---|---|---|---|---|
| Railroad Retirement / BUDGET INFORMATION / Tier Ia | `a` | Tier I benefits are based on time in covered railroad service and employment covered by Social Security. Benefits are adjusted each year by the full Social Security cost-of-living adjustment (COLA). | Tier Ia | `51306-2026-02-railroadretirement.xlsx` / `RailroadRetirement_02-2026` / R13C1 |
| Railroad Retirement / BUDGET INFORMATION / Tier IIb | `b` | Tier II benefits are for covered railroad service only. Benefits are adjusted each year by 32.5 percent of the annual Social Security COLA. | Tier IIb | `51306-2026-02-railroadretirement.xlsx` / `RailroadRetirement_02-2026` / R14C1 |
| Railroad Retirement / BUDGET INFORMATION / Supplemental Benefitsc | `c` | Supplemental benefits are for certain retirees who were hired before October 1981 and are not subject to COLAs. | Supplemental Benefitsc | `51306-2026-02-railroadretirement.xlsx` / `RailroadRetirement_02-2026` / R15C1 |
| Railroad Retirement / BUDGET INFORMATION / Vested Dual Benefitsd | `d` | Vested dual benefits are for certain retirees who were vested both in railroad retirement and in Social Security when railroad retirement benefits were restructured in 1974 and are not subject to COLAs. Outlays for those benefits are classified as discretionary spending. | Vested Dual Benefitsd | `51306-2026-02-railroadretirement.xlsx` / `RailroadRetirement_02-2026` / R16C1 |
| Railroad Retirement / BENEFICIARY INFORMATION | `e` | Railroad retirement annuitants may receive multiple components of benefits. This row shows the number of beneficiaries who receive at least one component, but with each beneficiary counted only once. | Number of Beneficiariese | `51306-2026-02-railroadretirement.xlsx` / `RailroadRetirement_02-2026` / R21C1 |

## is_total Interpretation

The `is_total` column flags rows whose `category` label contains the word 'total' or 'subtotal'. These rows summarise multiple line items and must be treated carefully in downstream analysis:

- **Summary views:** Include `is_total = true` rows to display headline figures.
- **Detailed aggregations:** Exclude `is_total = true` rows to prevent double-counting when summing across categories.
- **Time-series analysis:** Either filter is consistent as long as it is applied uniformly across all fiscal years being compared.
