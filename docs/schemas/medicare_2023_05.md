# Schema: Medicare 2023 05

- **Dataset:** `medicare_2023_05`
- **Vintage:** 2023-05
- **Rows:** 528
- **Fiscal years covered:** 2022–2033

## Purpose

Tidy long-form CBO baseline data for the **Medicare** program(s), extracted from CBO budget baseline workbooks published by the Congressional Budget Office. Each row represents one numeric source cell with explicit program, category hierarchy, period semantics, and cell-level provenance.

> **Aggregation caveat:** This dataset contains rows where `is_total = true`. These rows represent summary totals or subtotals drawn directly from the source worksheet. **Exclude `is_total = true` rows before summing across categories** to avoid double-counting.

## Provenance

| Field | Value |
|---|---|
| Source file(s) | `51302-2023-05-medicare.xlsx` |
| Source sheet(s) | `Medicare_05-2023` |
| Unit(s) | Billions of dollars, Millions of people, Percent |

## Columns

| Column | Type | Description | Unit | Example | Notes |
|---|---|---|---|---|---|
| `program` | string | Canonical CBO program name keyed by the stable source identifier. | N/A | `Medicare` | Stable across workbook vintages; use ``program_id`` as the machine key. |
| `category` | string | Leaf line-item label from the source worksheet. | N/A | `Mandatory Outlaysa` | Rows where ``is_total`` is ``true`` represent aggregated totals or subtotals and should be excluded from sum-based aggregations to avoid double-counting. |
| `fiscal_year` | integer or null | Annual federal fiscal year; blank for every other period type. | Year | `2022` | Historical actuals are retained. Consult ``period_type`` and the explicit period bounds before interpreting a row as annual fiscal-year data. |
| `value` | float | Parsed numeric value from the source cell. | See ``unit`` column | `975.0` | Negative values indicate outflows or reductions. Values originally enclosed in parentheses (e.g. ``(123)``) are converted to negative floats. |
| `unit` | string | Unit of measure for ``value``, resolved from row/section labels and parse metadata. | N/A | `Billions of dollars` | Common values include 'Millions of dollars', 'Billions of dollars', and 'Thousands'. |
| `source_file` | string | Original CBO workbook filename from ``data/raw/``. | N/A | `51302-2023-05-medicare.xlsx` | Use this column to trace any row back to its exact source workbook. |
| `source_sheet` | string | Worksheet name within the source workbook. | N/A | `Medicare_05-2023` | Combine with source file, row, and column for exact cell provenance. |
| `is_total` | boolean | ``true`` if the category label contains the word 'total' or 'subtotal', indicating an aggregated row. | N/A | `true` | **Always filter ``is_total = true`` rows out before computing sums or averages** across categories to avoid double-counting. Retain them for headline/summary views. |
| `program_id` | string | Stable numeric CBO identifier from the source filename. | N/A | `51302` | Preferred program join key across vintages. |
| `category_path` | string | Hierarchy-aware path from table/section headings to the leaf category. | N/A | `Medicare Totals / Mandatory Outlaysa` | Use this field instead of ``category`` when labels repeat in different subprograms. |
| `period_type` | string | Period semantics for the observation. | N/A | `fiscal_year` | Values include fiscal_year, calendar_year, award_year, school_year, cumulative_fiscal_years, and unmapped. |
| `period_start_year` | integer or null | First year represented by the source period. | Year | `2022` | Equals period_end_year for annual rows and is blank when the source period is not identified. |
| `period_end_year` | integer or null | Last year represented by the source period. | Year | `2022` | For annual fiscal-year rows this equals ``fiscal_year``. |
| `period_label` | string | Normalized source period label such as 2025 or 2025-2029. | N/A | `2022` | Rows with unrecognized periods are labeled explicitly rather than assigned a guessed year. |
| `source_row` | integer | One-based worksheet row containing the numeric source value. | N/A | `15` | Together with ``source_column`` identifies the exact source cell. |
| `source_column` | integer | One-based worksheet column containing the numeric source value. | N/A | `4` | Together with ``source_row`` identifies the exact source cell. |

## Variable Notes

Superscript letter markers are read from the source workbook's actual Excel rich-text formatting. Each extracted note is attached to every affected `category_path`; a note on a parent heading therefore applies to its child rows. A source-only entry is retained when the annotated source label has no emitted row in the processed dataset.

| Affected category path | Marker | `variable_note` | Source label | Source cell |
|---|---|---|---|---|
| Medicare Totals / Mandatory Outlaysa | `a` | Mandatory outlays include the effects of sequestration on spending for Medicare benefits under the Balanced Budget and Emergency Deficit Control Act of 1985, as amended. | Mandatory Outlaysa | `51302-2023-05-medicare.xlsx` / `Medicare_05-2023` / R15C1 |
| Medicare Totals / Total Offsetting Receiptsb | `b` | Offsetting receipts include premiums, rebates paid to the federal government by drug manufacturers whose products have prices that exceed an inflation-adjusted benchmark price, payments from states to Medicare Part D on behalf of enrollees who are eligible both for Medicare and for Medicaid, and amounts paid to providers and later recovered. | Total Offsetting Receiptsb | `51302-2023-05-medicare.xlsx` / `Medicare_05-2023` / R18C1 |
| Medicare / Benefits / Mandatory Administrationc | `c` | Mandatory outlays include those for quality improvement organizations, certain activities against fraud and abuse, and certain administrative activities funded in authorization acts. | Mandatory Administrationc | `51302-2023-05-medicare.xlsx` / `Medicare_05-2023` / R28C1 |
| Medicare / Components of Benefits / Group Plans (Includes Medicare Advantage)d | `d` | On February 1, 2023, CMS announced changes for calendar year 2024 that would result in slower growth in payments to MA plans than projected in CBO’s February 2023 baseline. On March 31, 2023, CMS announced that some of those changes would phase in over three years, along with other changes. Because of when its baseline was finalized, CBO’s updated projections reflect the changes announced on February 1, 2023, but not those announced on March 31, 2023. | Group Plans (Includes Medicare Advantage)d | `51302-2023-05-medicare.xlsx` / `Medicare_05-2023` / R37C1 |
| Medicare / Components of Benefits / Part De | `e` | Consists of payments to prescription drug plans and employer group waiver plans and for the retiree drug subsidy and the low-income subsidy. | Part De | `51302-2023-05-medicare.xlsx` / `Medicare_05-2023` / R38C1 |
| Medicare / Components of Benefits / Other Servicesf | `f` | Includes ambulance services, ambulatory surgical centers, community mental health centers, durable medical equipment, federally qualified health centers, hospice services, hospital outpatient services that are not paid for using the outpatient PPS, independent and physician in-office laboratory services, outpatient dialysis, outpatient therapy services, certain Part B prescription drugs, rural health clinic services, and the payment of Part B premiums for qualifying individuals. | Other Servicesf | `51302-2023-05-medicare.xlsx` / `Medicare_05-2023` / R40C1 |
| Medicare / Components of Offsetting Receipts / Part B Premiums and Inflation Rebate Collectionsg | `g` | Part B premium receipts include income-related premiums. | Part B Premiums and Inflation Rebate Collectionsg | `51302-2023-05-medicare.xlsx` / `Medicare_05-2023` / R45C1 |
| Medicare / Components of Offsetting Receipts / Part D Premiums and Inflation Rebate Collectionsh | `h` | Part D premium receipts include income-related premiums but not premiums that enrollees pay directly to their plans or premiums covered by the low-income subsidy. Under current law, the Secretary of the Department of Health and Human Services has the authority to delay until December 31, 2025, the invoicing of rebate amounts for Part D drug inflation rebates. As a result, CBO projects larger collections of those rebates in 2025. | Part D Premiums and Inflation Rebate Collectionsh | `51302-2023-05-medicare.xlsx` / `Medicare_05-2023` / R46C1 |
| Medicare / Components of Offsetting Receipts / Payments Recovered from Providersi,j | `i` | Recoveries are amounts that are paid to providers and later recovered; they are included in the total for mandatory Medicare spending. CBO counts the initial payment of such amounts as outlays for benefits and subsequent recoveries as offsetting receipts to conform to reporting in Monthly Treasury Statements. In the past, Medicare’s trustees have reported benefits net of recoveries; those reports have not treated the recoveries as offsetting receipts. | Payments Recovered from Providersi,j | `51302-2023-05-medicare.xlsx` / `Medicare_05-2023` / R48C1 |
| Medicare / Components of Offsetting Receipts / Payments Recovered from Providersi,j | `j` | The Accelerated and Advance Payment Program paid providers in advance of future claims. Those payments increased outlays in 2020. Recoupment of those payments is reflected as a recovery in 2021, 2022, and 2023. | Payments Recovered from Providersi,j | `51302-2023-05-medicare.xlsx` / `Medicare_05-2023` / R48C1 |
| Total / Memorandum: / Capitation Payments (Number per year)k | `k` | Capitation payments to group health plans and prescription drug plans for the month of October are shifted into the preceding fiscal year when October 1 falls on a weekend. | Capitation Payments (Number per year)k | `51302-2023-05-medicare.xlsx` / `Medicare_05-2023` / R57C1 |
| Total / Payment Updates and Changes in Price Indexes (Percent) / 10-Year Moving Average of Multifactor Productivityl | `l` | The inflation-based updates to payment rates for certain services and providers are adjusted by the 10-year moving average of multifactor productivity, including inpatient acute hospitals, skilled nursing facilities, long-term care hospitals, inpatient rehabilitation hospitals, home health agencies, psychiatric hospitals, hospice care, dialysis, outpatient hospitals, ambulance services, ambulatory surgical center services, and certain durable medical equipment. The adjustment for multifactor productivity is included in the PPS update factor shown above, as well as other legislated changes to the payment update. | 10-Year Moving Average of Multifactor Productivityl | `51302-2023-05-medicare.xlsx` / `Medicare_05-2023` / R62C1 |
| Total / Average Monthly Enrollment in a Fiscal Year (Millions of people) / Part Dm | `m` | Includes people enrolled in stand-alone prescription drug plans, MA plans with prescription drug coverage, employer group waiver plans, and the retiree drug subsidy. | Part Dm | `51302-2023-05-medicare.xlsx` / `Medicare_05-2023` / R67C1 |
| Total / Memorandum: / Group Plan Enrollmentn | `n` | Includes MA plans, cost contracts, and demonstration contracts covering Medicare Parts A and B. Does not include Health Care Prepayment Plans, which cover Part B services only. | Group Plan Enrollmentn | `51302-2023-05-medicare.xlsx` / `Medicare_05-2023` / R71C1 |

## is_total Interpretation

The `is_total` column flags rows whose `category` label contains the word 'total' or 'subtotal'. These rows summarise multiple line items and must be treated carefully in downstream analysis:

- **Summary views:** Include `is_total = true` rows to display headline figures.
- **Detailed aggregations:** Exclude `is_total = true` rows to prevent double-counting when summing across categories.
- **Time-series analysis:** Either filter is consistent as long as it is applied uniformly across all fiscal years being compared.
