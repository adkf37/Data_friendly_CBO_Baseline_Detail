# Schema: Medicare 2022 05

- **Dataset:** `medicare_2022_05`
- **Vintage:** 2022-05
- **Rows:** 511
- **Fiscal years covered:** 2021–2032

## Purpose

Tidy long-form CBO baseline data for the **Medicare** program(s), extracted from CBO budget baseline workbooks published by the Congressional Budget Office. Each row represents one numeric source cell with explicit program, category hierarchy, period semantics, and cell-level provenance.

> **Aggregation caveat:** This dataset contains rows where `is_total = true`. These rows represent summary totals or subtotals drawn directly from the source worksheet. **Exclude `is_total = true` rows before summing across categories** to avoid double-counting.

## Provenance

| Field | Value |
|---|---|
| Source file(s) | `51302-2022-05-medicare.xlsx` |
| Source sheet(s) | `Medicare_05-2022` |
| Unit(s) | Billions of dollars, Millions of people, Percent |

## Columns

| Column | Type | Description | Unit | Example | Notes |
|---|---|---|---|---|---|
| `program` | string | Canonical CBO program name keyed by the stable source identifier. | N/A | `Medicare` | Stable across workbook vintages; use ``program_id`` as the machine key. |
| `category` | string | Leaf line-item label from the source worksheet. | N/A | `Mandatory Outlaysa` | Rows where ``is_total`` is ``true`` represent aggregated totals or subtotals and should be excluded from sum-based aggregations to avoid double-counting. |
| `fiscal_year` | integer or null | Annual federal fiscal year; blank for every other period type. | Year | `2021` | Historical actuals are retained. Consult ``period_type`` and the explicit period bounds before interpreting a row as annual fiscal-year data. |
| `value` | float | Parsed numeric value from the source cell. | See ``unit`` column | `868.0` | Negative values indicate outflows or reductions. Values originally enclosed in parentheses (e.g. ``(123)``) are converted to negative floats. |
| `unit` | string | Unit of measure for ``value``, resolved from row/section labels and parse metadata. | N/A | `Billions of dollars` | Common values include 'Millions of dollars', 'Billions of dollars', and 'Thousands'. |
| `source_file` | string | Original CBO workbook filename from ``data/raw/``. | N/A | `51302-2022-05-medicare.xlsx` | Use this column to trace any row back to its exact source workbook. |
| `source_sheet` | string | Worksheet name within the source workbook. | N/A | `Medicare_05-2022` | Combine with source file, row, and column for exact cell provenance. |
| `is_total` | boolean | ``true`` if the category label contains the word 'total' or 'subtotal', indicating an aggregated row. | N/A | `true` | **Always filter ``is_total = true`` rows out before computing sums or averages** across categories to avoid double-counting. Retain them for headline/summary views. |
| `program_id` | string | Stable numeric CBO identifier from the source filename. | N/A | `51302` | Preferred program join key across vintages. |
| `category_path` | string | Hierarchy-aware path from table/section headings to the leaf category. | N/A | `Medicare Totals / Mandatory Outlaysa` | Use this field instead of ``category`` when labels repeat in different subprograms. |
| `period_type` | string | Period semantics for the observation. | N/A | `fiscal_year` | Values include fiscal_year, calendar_year, award_year, school_year, cumulative_fiscal_years, and unmapped. |
| `period_start_year` | integer or null | First year represented by the source period. | Year | `2021` | Equals period_end_year for annual rows and is blank when the source period is not identified. |
| `period_end_year` | integer or null | Last year represented by the source period. | Year | `2021` | For annual fiscal-year rows this equals ``fiscal_year``. |
| `period_label` | string | Normalized source period label such as 2025 or 2025-2029. | N/A | `2021` | Rows with unrecognized periods are labeled explicitly rather than assigned a guessed year. |
| `source_row` | integer | One-based worksheet row containing the numeric source value. | N/A | `15` | Together with ``source_column`` identifies the exact source cell. |
| `source_column` | integer | One-based worksheet column containing the numeric source value. | N/A | `4` | Together with ``source_row`` identifies the exact source cell. |

## Variable Notes

Superscript letter markers are read from the source workbook's actual Excel rich-text formatting. Each extracted note is attached to every affected `category_path`; a note on a parent heading therefore applies to its child rows. A source-only entry is retained when the annotated source label has no emitted row in the processed dataset.

| Affected category path | Marker | `variable_note` | Source label | Source cell |
|---|---|---|---|---|
| Medicare Totals / Mandatory Outlaysa | `a` | Mandatory outlays include the effects of sequestration under the Balanced Budget and Emergency Deficit Control Act of 1985, as amended, on spending for Medicare benefits. | Mandatory Outlaysa | `51302-2022-05-medicare.xlsx` / `Medicare_05-2022` / R15C1 |
| Medicare Totals / Total Offsetting Receiptsb | `b` | Offsetting receipts include premiums, amounts paid to providers and later recovered, and phased-down state contribution (clawback) payments from the states to Part D. | Total Offsetting Receiptsb | `51302-2022-05-medicare.xlsx` / `Medicare_05-2022` / R18C1 |
| Medicare / Benefits / Part Dc | `c` | The projections for Part D benefits include the estimated effects of a final rule that would eliminate safe-harbor protections for post-sale rebates paid by pharmaceutical manufacturers to health plans and pharmacy benefit managers in Medicare Part D beginning on January 1, 2026. They also include the estimated effects of a rule that would require certain pharmacy price concessions to be reflected at the point of sale in Medicare Part D. At the time of analysis, the rule had been proposed but not finalized. The proposed rule had an implementation date of January 1, 2023. In accordance with CBO’s standard practice for incorporating the effects of proposed rules in its baseline projections, these projections reflect the assumption that there is a 50 percent chance that the rule would be finalized and take effect in 2023. After work on the baseline had been completed, CMS finalized the rule with an implementation date of January 1, 2024. | Part Dc | `51302-2022-05-medicare.xlsx` / `Medicare_05-2022` / R26C1 |
| Medicare / Benefits / Mandatory Administrationd | `d` | Mandatory outlays for quality improvement organizations, certain activities against fraud and abuse, and certain administrative activities. | Mandatory Administrationd | `51302-2022-05-medicare.xlsx` / `Medicare_05-2022` / R28C1 |
| Medicare / Components of Benefits / Part De | `e` | Includes payments to prescription drug plans and employer group waiver plans, and for the retiree drug subsidy and the low-income subsidy. The low-income subsidy line is a component of total Part D outlays. | Part De | `51302-2022-05-medicare.xlsx` / `Medicare_05-2022` / R38C1 |
| Medicare / Components of Benefits / Other servicesf | `f` | Includes ambulance services, ambulatory surgical centers, community mental health centers, durable medical equipment, federally qualified health centers, hospice services, hospital outpatient services that are not paid for using the outpatient PPS, independent and physician in-office laboratory services, outpatient dialysis, outpatient therapy services, certain Part B prescription drugs, rural health clinic services, and the payment of Part B premiums for beneficiaries in the Qualifying Individuals program. | Other servicesf | `51302-2022-05-medicare.xlsx` / `Medicare_05-2022` / R40C1 |
| Medicare / Components of Offsetting Receipts / Part B Premiumsg | `g` | Part B premium receipts include income-related premiums. | Part B Premiumsg | `51302-2022-05-medicare.xlsx` / `Medicare_05-2022` / R45C1 |
| Medicare / Components of Offsetting Receipts / Part D Premiumsh | `h` | Part D premium receipts include income-related premiums but not premiums that enrollees pay directly to their plans or premiums covered by the low-income subsidy. | Part D Premiumsh | `51302-2022-05-medicare.xlsx` / `Medicare_05-2022` / R46C1 |
| Medicare / Components of Offsetting Receipts / Payments Recovered from Providersi | `i` | Recoveries are amounts that are paid to providers and later recovered; they are included in the total for mandatory Medicare spending. CBO counts the initial payment of such amounts as outlays for benefits and subsequent recoveries as offsetting receipts to conform to reporting in the Monthly Treasury Statements. In the past, Medicare’s trustees have reported benefits net of recoveries; those reports have not treated the recoveries as offsetting receipts. In 2020, Medicare paid providers in advance of future claims through the Accelerated and Advance Payments Program. Recoupments of those payments are reflected as recoveries in 2021 and 2022. | Payments Recovered from Providersi | `51302-2022-05-medicare.xlsx` / `Medicare_05-2022` / R48C1 |
| Total / Memorandum: / Capitation Payments (Number per year)j | `j` | Capitation payments to group health plans and prescription drug plans for the month of October are shifted into the preceding fiscal year when October 1 falls on a weekend. The adjustment for timing shifts reflects 12 capitation payments per year. | Capitation Payments (Number per year)j | `51302-2022-05-medicare.xlsx` / `Medicare_05-2022` / R57C1 |
| Total / Payment Updates and Changes in Price Indexes (Percent) / 10-Year Moving Average of Multifactor Productivityk | `k` | The inflation-based updates to payment rates for certain services and providers are adjusted by the 10-year moving average of multifactor productivity. Those providers and services include inpatient acute hospitals, skilled nursing facilities, long-term care hospitals, inpatient rehabilitation hospitals, home health agencies, psychiatric hospitals, hospice care, physician services, dialysis, outpatient hospitals, ambulance services, ambulatory surgical center services, laboratory services, and certain durable medical equipment. The adjustment for multifactor productivity is included in the PPS update factor shown above, as well as other legislated changes to the payment update. | 10-Year Moving Average of Multifactor Productivityk | `51302-2022-05-medicare.xlsx` / `Medicare_05-2022` / R62C1 |
| Total / Average Monthly Enrollment in a Fiscal Year (Millions of people) / Part Dl | `l` | Includes people enrolled in stand-alone prescription drug plans, Medicare Advantage plans with prescription drug coverage, employer group waiver plans, and the retiree drug subsidy. | Part Dl | `51302-2022-05-medicare.xlsx` / `Medicare_05-2022` / R67C1 |
| Total / Memorandum: / Group Plan Enrollmentm | `m` | Includes Medicare Advantage, cost contracts, and demonstration contracts covering Medicare Parts A and B. Does not include Health Care Prepayment Plans, which cover Part B services only. | Group Plan Enrollmentm | `51302-2022-05-medicare.xlsx` / `Medicare_05-2022` / R71C1 |

## is_total Interpretation

The `is_total` column flags rows whose `category` label contains the word 'total' or 'subtotal'. These rows summarise multiple line items and must be treated carefully in downstream analysis:

- **Summary views:** Include `is_total = true` rows to display headline figures.
- **Detailed aggregations:** Exclude `is_total = true` rows to prevent double-counting when summing across categories.
- **Time-series analysis:** Either filter is consistent as long as it is applied uniformly across all fiscal years being compared.
