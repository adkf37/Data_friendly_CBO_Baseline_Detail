# Schema: Mortgages 2021 07

- **Dataset:** `mortgages_2021_07`
- **Vintage:** 2021-07
- **Rows:** 153
- **Fiscal years covered:** 2021–2031

## Purpose

Tidy long-form CBO baseline data for the **Mortgages** program(s), extracted from CBO budget baseline workbooks published by the Congressional Budget Office. Each row represents one numeric source cell with explicit program, category hierarchy, period semantics, and cell-level provenance.

## Provenance

| Field | Value |
|---|---|
| Source file(s) | `51297-2021-07-mortgages.xlsx` |
| Source sheet(s) | `Mortgages_07-2021` |
| Unit(s) | Millions of dollars, Percent |

## Columns

| Column | Type | Description | Unit | Example | Notes |
|---|---|---|---|---|---|
| `program` | string | Canonical CBO program name keyed by the stable source identifier. | N/A | `Mortgages` | Stable across workbook vintages; use ``program_id`` as the machine key. |
| `category` | string | Leaf line-item label from the source worksheet. | N/A | `Value of Mortgage Originations` | Rows where ``is_total`` is ``true`` represent aggregated totals or subtotals and should be excluded from sum-based aggregations to avoid double-counting. |
| `fiscal_year` | integer or null | Annual federal fiscal year; blank for every other period type. | Year | `2021` | Historical actuals are retained. Consult ``period_type`` and the explicit period bounds before interpreting a row as annual fiscal-year data. |
| `value` | float | Parsed numeric value from the source cell. | See ``unit`` column | `4129000.0` | Negative values indicate outflows or reductions. Values originally enclosed in parentheses (e.g. ``(123)``) are converted to negative floats. |
| `unit` | string | Unit of measure for ``value``, resolved from row/section labels and parse metadata. | N/A | `Millions of dollars` | Common values include 'Millions of dollars', 'Billions of dollars', and 'Thousands'. |
| `source_file` | string | Original CBO workbook filename from ``data/raw/``. | N/A | `51297-2021-07-mortgages.xlsx` | Use this column to trace any row back to its exact source workbook. |
| `source_sheet` | string | Worksheet name within the source workbook. | N/A | `Mortgages_07-2021` | Combine with source file, row, and column for exact cell provenance. |
| `is_total` | boolean | ``true`` if the category label contains the word 'total' or 'subtotal', indicating an aggregated row. | N/A | `false` | **Always filter ``is_total = true`` rows out before computing sums or averages** across categories to avoid double-counting. Retain them for headline/summary views. |
| `program_id` | string | Stable numeric CBO identifier from the source filename. | N/A | `51297` | Preferred program join key across vintages. |
| `category_path` | string | Hierarchy-aware path from table/section headings to the leaf category. | N/A | `Federal Programs That Guarantee Mortg...` | Use this field instead of ``category`` when labels repeat in different subprograms. |
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
| Federal Programs That Guarantee Mortgages / Fannie Mae and Freddie Mac / Annual Subsidy Costsa | `a` | For 2022 through 2031, the baseline includes projected subsidy costs of new mortgage loans and guarantees made by Fannie Mae and Freddie Mac in each year, estimated on a fair-value basis. For more information about CBO's budgetary treatment of Fannie Mae and Freddie Mac, see Congressional Budget Office, CBO’s Budgetary Treatment of Fannie Mae and Freddie Mac (January 2010), www.cbo.gov/publication/41887. | Annual Subsidy Costsa | `51297-2021-07-mortgages.xlsx` / `Mortgages_07-2021` / R18C3 |
| Federal Programs That Guarantee Mortgages / Fannie Mae and Freddie Mac / Cash Receiptsb | `b` | For fiscal year 2021, the baseline includes an estimate of mandatory cash payments from Fannie Mae and Freddie Mac to the Treasury. | Cash Receiptsb | `51297-2021-07-mortgages.xlsx` / `Mortgages_07-2021` / R19C3 |
| Federal Programs That Guarantee Mortgages / Federal Housing Administration MMI Programc / Annual Subsidy Costs | `c` | Excludes Home Equity Conversion Mortgages; MMI subsidy receipts are recorded in the budget as offsetting collections to discretionary appropriations. The subsidy rate for the MMI program is calculated using FCRA methods. | Federal Housing Administration MMI Programc | `51297-2021-07-mortgages.xlsx` / `Mortgages_07-2021` / R23C2 |
| Federal Programs That Guarantee Mortgages / Federal Housing Administration MMI Programc / Share of Originations (Percent) | `c` | Excludes Home Equity Conversion Mortgages; MMI subsidy receipts are recorded in the budget as offsetting collections to discretionary appropriations. The subsidy rate for the MMI program is calculated using FCRA methods. | Federal Housing Administration MMI Programc | `51297-2021-07-mortgages.xlsx` / `Mortgages_07-2021` / R23C2 |
| Federal Programs That Guarantee Mortgages / Federal Housing Administration MMI Programc / Subsidy Rate (Percent) | `c` | Excludes Home Equity Conversion Mortgages; MMI subsidy receipts are recorded in the budget as offsetting collections to discretionary appropriations. The subsidy rate for the MMI program is calculated using FCRA methods. | Federal Housing Administration MMI Programc | `51297-2021-07-mortgages.xlsx` / `Mortgages_07-2021` / R23C2 |
| Federal Programs That Guarantee Mortgages / Federal Housing Administration MMI Programc / Value of Annual Loans | `c` | Excludes Home Equity Conversion Mortgages; MMI subsidy receipts are recorded in the budget as offsetting collections to discretionary appropriations. The subsidy rate for the MMI program is calculated using FCRA methods. | Federal Housing Administration MMI Programc | `51297-2021-07-mortgages.xlsx` / `Mortgages_07-2021` / R23C2 |
| Federal Programs That Guarantee Mortgages / Department of Veterans Affairs Home Loan Programd / Annual Subsidy Costs | `d` | Includes guaranteed loans and direct loans made by VA on homes sold by the department; excludes loans acquired from other lenders and guarantees on securities of direct loans originated by VA. Costs associated with this program are recorded in the budget as mandatory spending. The subsidy rate for the VA program is calculated using FCRA methods. | Department of Veterans Affairs Home Loan Programd | `51297-2021-07-mortgages.xlsx` / `Mortgages_07-2021` / R29C2 |
| Federal Programs That Guarantee Mortgages / Department of Veterans Affairs Home Loan Programd / Share of Originations (Percent) | `d` | Includes guaranteed loans and direct loans made by VA on homes sold by the department; excludes loans acquired from other lenders and guarantees on securities of direct loans originated by VA. Costs associated with this program are recorded in the budget as mandatory spending. The subsidy rate for the VA program is calculated using FCRA methods. | Department of Veterans Affairs Home Loan Programd | `51297-2021-07-mortgages.xlsx` / `Mortgages_07-2021` / R29C2 |
| Federal Programs That Guarantee Mortgages / Department of Veterans Affairs Home Loan Programd / Subsidy Rate (Percent) | `d` | Includes guaranteed loans and direct loans made by VA on homes sold by the department; excludes loans acquired from other lenders and guarantees on securities of direct loans originated by VA. Costs associated with this program are recorded in the budget as mandatory spending. The subsidy rate for the VA program is calculated using FCRA methods. | Department of Veterans Affairs Home Loan Programd | `51297-2021-07-mortgages.xlsx` / `Mortgages_07-2021` / R29C2 |
| Federal Programs That Guarantee Mortgages / Department of Veterans Affairs Home Loan Programd / Value of Annual Loans | `d` | Includes guaranteed loans and direct loans made by VA on homes sold by the department; excludes loans acquired from other lenders and guarantees on securities of direct loans originated by VA. Costs associated with this program are recorded in the budget as mandatory spending. The subsidy rate for the VA program is calculated using FCRA methods. | Department of Veterans Affairs Home Loan Programd | `51297-2021-07-mortgages.xlsx` / `Mortgages_07-2021` / R29C2 |
| Federal Programs That Guarantee Mortgages / Mortgage-Backed Securities Programe / Annual Subsidy Receipts | `e` | GNMA securitizes more than 90 percent of FHA’s MMI loan guarantees and 98 percent of VA’s loan guarantees, resulting in additional offsetting collections. The subsidy rate for GNMA, which is calculated using FCRA methods, is estimated to be -0.31 percent in 2021 and -0.38 percent annually over the 2022-2031 period. | Mortgage-Backed Securities Programe | `51297-2021-07-mortgages.xlsx` / `Mortgages_07-2021` / R36C2 |

## is_total Interpretation

The `is_total` column flags rows whose `category` label contains the word 'total' or 'subtotal'. These rows summarise multiple line items and must be treated carefully in downstream analysis:

- **Summary views:** Include `is_total = true` rows to display headline figures.
- **Detailed aggregations:** Exclude `is_total = true` rows to prevent double-counting when summing across categories.
- **Time-series analysis:** Either filter is consistent as long as it is applied uniformly across all fiscal years being compared.
