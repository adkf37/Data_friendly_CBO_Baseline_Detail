# Schema: Militaryretirement 0 2022 05

**Dataset:** `militaryretirement_0_2022_05`  
**Vintage:** 2022-05  
**Rows:** 96  
**Fiscal years covered:** 2022–2032  

## Purpose

Tidy long-form CBO baseline data for the **Militaryretirement 0** program(s), extracted from CBO budget baseline workbooks published by the Congressional Budget Office. Each row represents a single program/category/fiscal-year observation.

## Provenance

| Field | Value |
|---|---|
| Source file(s) | `51303-2022-05-militaryretirement_0.xlsx` |
| Source sheet(s) | `Mil Retirement_5-2022` |
| Unit(s) | Billions of dollars, Dollars per participant, Thousands of people |

## Columns

| Column | Type | Description | Unit | Example | Notes |
|---|---|---|---|---|---|
| `program` | string | CBO program name inferred from the source workbook filename. | N/A | `Militaryretirement 0` | Derived from the workbook filename; may include a version suffix for older files. |
| `category` | string | Line-item label as it appears in the source worksheet after header normalization. | N/A | `Budget Authority` | Rows where ``is_total`` is ``true`` represent aggregated totals or subtotals and should be excluded from sum-based aggregations to avoid double-counting. |
| `fiscal_year` | integer | Federal fiscal year to which the value applies (Oct 1 – Sep 30). | Year | `2022` | Only years in the range 2019–2040 are included; historical prior-year columns outside that range are silently dropped by the transform. |
| `value` | float | Parsed numeric value from the source cell. | See ``unit`` column | `67.0` | Negative values indicate outflows or reductions. Values originally enclosed in parentheses (e.g. ``(123)``) are converted to negative floats. |
| `unit` | string | Unit of measure for the ``value`` column, sourced from the parse plan. | N/A | `Billions of dollars` | Common values include 'Millions of dollars', 'Billions of dollars', and 'Thousands'. |
| `source_file` | string | Original CBO workbook filename from ``data/raw/``. | N/A | `51303-2022-05-militaryretirement_0.xlsx` | Use this column to trace any row back to its exact source workbook. |
| `source_sheet` | string | Worksheet name within the source workbook. | N/A | `Mil Retirement_5-2022` | Combine with ``source_file`` for a fully qualified provenance reference. |
| `is_total` | boolean | ``true`` if the category label contains the word 'total' or 'subtotal', indicating an aggregated row. | N/A | `false` | **Always filter ``is_total = true`` rows out before computing sums or averages** across categories to avoid double-counting. Retain them for headline/summary views. |

## is_total Interpretation

The `is_total` column flags rows whose `category` label contains the word 'total' or 'subtotal'. These rows summarise multiple line items and must be treated carefully in downstream analysis:

- **Summary views:** Include `is_total = true` rows to display headline figures.
- **Detailed aggregations:** Exclude `is_total = true` rows to prevent double-counting when summing across categories.
- **Time-series analysis:** Either filter is consistent as long as it is applied uniformly across all fiscal years being compared.
