# Task: Transform Excel Files to Tidy CSVs

**ID:** task-03-transform  
**Phase:** Build  
**Owner:** Data Engineer  
**Priority:** High (core deliverable)  
**Estimated Effort:** Large (multi-day, iterative per program group)

---

## Objective

For each Excel file in `data/raw/`, parse every data sheet and produce one or more tidy (long-format) CSVs in `data/processed/`. Each row in a processed CSV represents a single observation: one program, one category, one fiscal year, one value.

## Acceptance Criteria

- [ ] Script `src/transform.py` (or modular `src/transformers/<program>.py` files) exists and is runnable.
- [ ] Every Excel data sheet produces at least one corresponding CSV in `data/processed/`.
- [ ] Output CSVs conform to the standard schema:

  | Column | Type | Description |
  |---|---|---|
  | `program` | string | CBO program name (e.g., "Medicaid") |
  | `category` | string | Sub-category or line item label |
  | `fiscal_year` | integer | Fiscal year (e.g., 2025) |
  | `value` | float | Numeric value |
  | `unit` | string | Unit of measure (e.g., "billions of dollars") |
  | `source_file` | string | Original Excel filename |
  | `source_sheet` | string | Original sheet name |
  | `is_total` | boolean | True if the row represents a total or subtotal line |

- [ ] No wide/pivot format; all year columns are melted into `fiscal_year`/`value` rows.
- [ ] Merged cells in headers are forward-filled correctly.
- [ ] Rows that are totals or subtotals are flagged with a boolean `is_total` column.
- [ ] Empty rows and footnote rows are dropped.
- [ ] Processed CSVs are saved as UTF-8 encoded files.

## Implementation Notes

- Use `pandas` with `openpyxl` engine for reading.
- Handle programs individually where header structures differ significantly.
- Log a warning (do not fail) when a sheet cannot be parsed; record it in a `data/processed/parse_errors.log`.
- Prefer general-purpose parsing logic; write program-specific overrides only when necessary.

## Dependencies

- task-02-inspect (profile report guides implementation)

## Test Approach

- For each program, assert output CSV is non-empty and has the required columns.
- For each program, assert `fiscal_year` values are integers in plausible range (e.g., 2000–2040).
- For each program, assert no duplicate rows (program + category + fiscal_year must be unique, or document exceptions).
