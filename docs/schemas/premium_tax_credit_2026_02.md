# Schema: Premium TAX Credit 2026 02

- **Dataset:** `premium_tax_credit_2026_02`
- **Vintage:** 2026-02
- **Rows:** 144
- **Fiscal years covered:** 2026–2036

## Purpose

Tidy long-form CBO baseline data for the **Premium Tax Credit** program(s), extracted from CBO budget baseline workbooks published by the Congressional Budget Office. Each row represents one numeric source cell with explicit program, category hierarchy, period semantics, and cell-level provenance.

> **Aggregation caveat:** This dataset contains rows where `is_total = true`. These rows represent summary totals or subtotals drawn directly from the source worksheet. **Exclude `is_total = true` rows before summing across categories** to avoid double-counting.

## Provenance

| Field | Value |
|---|---|
| Source file(s) | `60523-2026-02-premium-tax-credit.xlsx` |
| Source sheet(s) | `PTC_02-2026` |
| Unit(s) | Billions of dollars, Millions of people |

## Columns

| Column | Type | Description | Unit | Example | Notes |
|---|---|---|---|---|---|
| `program` | string | Canonical CBO program name keyed by the stable source identifier. | N/A | `Premium Tax Credit` | Stable across workbook vintages; use ``program_id`` as the machine key. |
| `category` | string | Leaf line-item label from the source worksheet. | N/A | `Outlays for the premium tax credita` | Rows where ``is_total`` is ``true`` represent aggregated totals or subtotals and should be excluded from sum-based aggregations to avoid double-counting. |
| `fiscal_year` | integer or null | Annual federal fiscal year; blank for every other period type. | Year | `2026` | Historical actuals are retained. Consult ``period_type`` and the explicit period bounds before interpreting a row as annual fiscal-year data. |
| `value` | float | Parsed numeric value from the source cell. | See ``unit`` column | `88.0` | Negative values indicate outflows or reductions. Values originally enclosed in parentheses (e.g. ``(123)``) are converted to negative floats. |
| `unit` | string | Unit of measure for ``value``, resolved from row/section labels and parse metadata. | N/A | `Billions of dollars` | Common values include 'Millions of dollars', 'Billions of dollars', and 'Thousands'. |
| `source_file` | string | Original CBO workbook filename from ``data/raw/``. | N/A | `60523-2026-02-premium-tax-credit.xlsx` | Use this column to trace any row back to its exact source workbook. |
| `source_sheet` | string | Worksheet name within the source workbook. | N/A | `PTC_02-2026` | Combine with source file, row, and column for exact cell provenance. |
| `is_total` | boolean | ``true`` if the category label contains the word 'total' or 'subtotal', indicating an aggregated row. | N/A | `false` | **Always filter ``is_total = true`` rows out before computing sums or averages** across categories to avoid double-counting. Retain them for headline/summary views. |
| `program_id` | string | Stable numeric CBO identifier from the source filename. | N/A | `60523` | Preferred program join key across vintages. |
| `category_path` | string | Hierarchy-aware path from table/section headings to the leaf category. | N/A | `Premium Tax Credit and Related Spendi...` | Use this field instead of ``category`` when labels repeat in different subprograms. |
| `period_type` | string | Period semantics for the observation. | N/A | `fiscal_year` | Values include fiscal_year, calendar_year, award_year, school_year, cumulative_fiscal_years, and unmapped. |
| `period_start_year` | integer or null | First year represented by the source period. | Year | `2026` | Equals period_end_year for annual rows and is blank when the source period is not identified. |
| `period_end_year` | integer or null | Last year represented by the source period. | Year | `2026` | For annual fiscal-year rows this equals ``fiscal_year``. |
| `period_label` | string | Normalized source period label such as 2025 or 2025-2029. | N/A | `2026` | Rows with unrecognized periods are labeled explicitly rather than assigned a guessed year. |
| `source_row` | integer | One-based worksheet row containing the numeric source value. | N/A | `14` | Together with ``source_column`` identifies the exact source cell. |
| `source_column` | integer | One-based worksheet column containing the numeric source value. | N/A | `4` | Together with ``source_row`` identifies the exact source cell. |

## Variable Notes

Superscript letter markers are read from the source workbook's actual Excel rich-text formatting. Each extracted note is attached to every affected `category_path`; a note on a parent heading therefore applies to its child rows. A source-only entry is retained when the annotated source label has no emitted row in the processed dataset.

| Affected category path | Marker | `variable_note` | Source label | Source cell |
|---|---|---|---|---|
| Premium Tax Credit and Related Spending / Outlays for the premium tax credita | `a` | Estimates are preliminary and subject to revision. | Outlays for the premium tax credita | `60523-2026-02-premium-tax-credit.xlsx` / `PTC_02-2026` / R14C2 |
| Premium Tax Credit and Related Spending / Revenue reductions from the premium tax credita | `a` | Estimates are preliminary and subject to revision. | Revenue reductions from the premium tax credita | `60523-2026-02-premium-tax-credit.xlsx` / `PTC_02-2026` / R15C2 |
| Premium Tax Credit and Related Spending / Basic Health Programb, c / Collections for risk adjustmentd | `b` | Section 1332 of the ACA allows states to apply for federal waivers for some of the act’s rules governing insurance markets and to receive federal assistance in paying for programs that offer health insurance. To obtain a waiver, a state’s proposal must be budget neutral and must provide insurance coverage that is comparable to coverage required by the ACA. | Basic Health Programb, c | `60523-2026-02-premium-tax-credit.xlsx` / `PTC_02-2026` / R17C2 |
| Premium Tax Credit and Related Spending / Basic Health Programb, c / Collections for risk adjustmentd | `c` | The Basic Health Program allows states to establish a coverage program primarily for people whose income is between 138 percent and 200 percent of the federal poverty level. The federal government provides states with funding equal to 95 percent of the amount in subsidies for which enrollees would otherwise have been eligible through a marketplace. Only the District of Columbia, Minnesota, and Oregon currently operate such programs. Estimates include enrollment in New York’s Essential Plan, which is funded through a section 1332 waiver and mirrors the Basic Health Program, with eligibility up to 250 percent of the federal poverty level. New York’s Essential Plan is anticipated to transition to the Basic Health Program in 2026. | Basic Health Programb, c | `60523-2026-02-premium-tax-credit.xlsx` / `PTC_02-2026` / R17C2 |
| Premium Tax Credit and Related Spending / Basic Health Programb, c / Payments for risk adjustmentd | `b` | Section 1332 of the ACA allows states to apply for federal waivers for some of the act’s rules governing insurance markets and to receive federal assistance in paying for programs that offer health insurance. To obtain a waiver, a state’s proposal must be budget neutral and must provide insurance coverage that is comparable to coverage required by the ACA. | Basic Health Programb, c | `60523-2026-02-premium-tax-credit.xlsx` / `PTC_02-2026` / R17C2 |
| Premium Tax Credit and Related Spending / Basic Health Programb, c / Payments for risk adjustmentd | `c` | The Basic Health Program allows states to establish a coverage program primarily for people whose income is between 138 percent and 200 percent of the federal poverty level. The federal government provides states with funding equal to 95 percent of the amount in subsidies for which enrollees would otherwise have been eligible through a marketplace. Only the District of Columbia, Minnesota, and Oregon currently operate such programs. Estimates include enrollment in New York’s Essential Plan, which is funded through a section 1332 waiver and mirrors the Basic Health Program, with eligibility up to 250 percent of the federal poverty level. New York’s Essential Plan is anticipated to transition to the Basic Health Program in 2026. | Basic Health Programb, c | `60523-2026-02-premium-tax-credit.xlsx` / `PTC_02-2026` / R17C2 |
| Premium Tax Credit and Related Spending / Basic Health Programb, c / Total | `b` | Section 1332 of the ACA allows states to apply for federal waivers for some of the act’s rules governing insurance markets and to receive federal assistance in paying for programs that offer health insurance. To obtain a waiver, a state’s proposal must be budget neutral and must provide insurance coverage that is comparable to coverage required by the ACA. | Basic Health Programb, c | `60523-2026-02-premium-tax-credit.xlsx` / `PTC_02-2026` / R17C2 |
| Premium Tax Credit and Related Spending / Basic Health Programb, c / Total | `c` | The Basic Health Program allows states to establish a coverage program primarily for people whose income is between 138 percent and 200 percent of the federal poverty level. The federal government provides states with funding equal to 95 percent of the amount in subsidies for which enrollees would otherwise have been eligible through a marketplace. Only the District of Columbia, Minnesota, and Oregon currently operate such programs. Estimates include enrollment in New York’s Essential Plan, which is funded through a section 1332 waiver and mirrors the Basic Health Program, with eligibility up to 250 percent of the federal poverty level. New York’s Essential Plan is anticipated to transition to the Basic Health Program in 2026. | Basic Health Programb, c | `60523-2026-02-premium-tax-credit.xlsx` / `PTC_02-2026` / R17C2 |
| Premium Tax Credit and Related Spending / Basic Health Programb, c / Collections for risk adjustmentd | `d` | The risk adjustment program is intended to stabilize premiums in the nongroup and small-group markets. The federal government collects fees from insurers with enrollees who are relatively more healthy and makes roughly offsetting payments to insurers with enrollees who are relatively less healthy. | Collections for risk adjustmentd | `60523-2026-02-premium-tax-credit.xlsx` / `PTC_02-2026` / R18C2 |
| Premium Tax Credit and Related Spending / Basic Health Programb, c / Payments for risk adjustmentd | `d` | The risk adjustment program is intended to stabilize premiums in the nongroup and small-group markets. The federal government collects fees from insurers with enrollees who are relatively more healthy and makes roughly offsetting payments to insurers with enrollees who are relatively less healthy. | Payments for risk adjustmentd | `60523-2026-02-premium-tax-credit.xlsx` / `PTC_02-2026` / R19C2 |
| Premium Tax Credit and Related Spending / Enrollment Through ACA Marketplacese / Basic Health Program Enrollmentc | `e` | The marketplaces established under the ACA are operated by the federal government, state governments, or partnerships between the two. | Enrollment Through ACA Marketplacese | `60523-2026-02-premium-tax-credit.xlsx` / `PTC_02-2026` / R26C1 |
| Premium Tax Credit and Related Spending / Enrollment Through ACA Marketplacese / Subsidized | `e` | The marketplaces established under the ACA are operated by the federal government, state governments, or partnerships between the two. | Enrollment Through ACA Marketplacese | `60523-2026-02-premium-tax-credit.xlsx` / `PTC_02-2026` / R26C1 |
| Premium Tax Credit and Related Spending / Enrollment Through ACA Marketplacese / Total, Enrollment Through ACA Marketplaces | `e` | The marketplaces established under the ACA are operated by the federal government, state governments, or partnerships between the two. | Enrollment Through ACA Marketplacese | `60523-2026-02-premium-tax-credit.xlsx` / `PTC_02-2026` / R26C1 |
| Premium Tax Credit and Related Spending / Enrollment Through ACA Marketplacese / Unsubsidized | `e` | The marketplaces established under the ACA are operated by the federal government, state governments, or partnerships between the two. | Enrollment Through ACA Marketplacese | `60523-2026-02-premium-tax-credit.xlsx` / `PTC_02-2026` / R26C1 |
| Premium Tax Credit and Related Spending / Enrollment Through ACA Marketplacese / Basic Health Program Enrollmentc | `c` | The Basic Health Program allows states to establish a coverage program primarily for people whose income is between 138 percent and 200 percent of the federal poverty level. The federal government provides states with funding equal to 95 percent of the amount in subsidies for which enrollees would otherwise have been eligible through a marketplace. Only the District of Columbia, Minnesota, and Oregon currently operate such programs. Estimates include enrollment in New York’s Essential Plan, which is funded through a section 1332 waiver and mirrors the Basic Health Program, with eligibility up to 250 percent of the federal poverty level. New York’s Essential Plan is anticipated to transition to the Basic Health Program in 2026. | Basic Health Program Enrollmentc | `60523-2026-02-premium-tax-credit.xlsx` / `PTC_02-2026` / R31C1 |
| Premium Tax Credit and Related Spending / Nationwide Average Annual Benchmark Premium for a / 21-Year-Old ACA Marketplace Enrolleef | `f` | The premium for a 21-year-old is used in determining the maximum premium variation allowed by age. (Premiums for a 64-year-old may not exceed three times the premium for a 21-year-old.) | 21-Year-Old ACA Marketplace Enrolleef | `60523-2026-02-premium-tax-credit.xlsx` / `PTC_02-2026` / R38C2 |

## is_total Interpretation

The `is_total` column flags rows whose `category` label contains the word 'total' or 'subtotal'. These rows summarise multiple line items and must be treated carefully in downstream analysis:

- **Summary views:** Include `is_total = true` rows to display headline figures.
- **Detailed aggregations:** Exclude `is_total = true` rows to prevent double-counting when summing across categories.
- **Time-series analysis:** Either filter is consistent as long as it is applied uniformly across all fiscal years being compared.
