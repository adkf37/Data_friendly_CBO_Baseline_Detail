# Task: Transform Excel Files to Tidy CSVs

**ID:** task-03-transform  
**Phase:** Build  
**Owner:** Data Engineer  
**Reviewers:** Lead, Tester  
**Priority:** High (core deliverable)  
**Estimated Effort:** Large (iterative by program group)

---

## Objective

Use the workbook parse plan to convert CBO Excel sheets into tidy UTF-8 CSV datasets in `data/processed/`, preserving enough provenance for later schema generation and reconciliation.

## Inputs

- `data/raw/*.xlsx`
- `config/workbook_parse_plan.yaml`
- Design decisions from `.squad/decisions.md`

## Outputs

- `src/transform.py` and any supporting modules under `src/transformers/`
- `data/processed/*.csv`
- `data/processed/parse_errors.log`

## Execution Slices

Implement and validate this task in three slices so build work stays reviewable:

1. Health programs
2. Income security programs
3. Remaining programs

Each slice should update `.squad/decisions.md` with any new parser overrides before moving to the next slice.

## Required Workflow

1. Read parse-plan entries and skip sheets explicitly marked `include: false`.
2. Normalize headers, including forward-filling merged header cells where needed.
3. Reshape year columns into long form with one row per program/category/fiscal year.
4. Preserve provenance in every row:

   | Column | Type | Description |
   |---|---|---|
   | `program` | string | CBO program name |
   | `category` | string | Line-item label after header normalization |
   | `fiscal_year` | integer | Fiscal year |
   | `value` | float | Parsed numeric value |
   | `unit` | string | Unit of measure |
   | `source_file` | string | Original workbook filename |
   | `source_sheet` | string | Original sheet name |
   | `is_total` | boolean | Whether the row is a total or subtotal |

5. Name output datasets according to `output_dataset` in the parse plan so schema and verification steps have stable targets.
6. Write parse failures to `data/processed/parse_errors.log`; do not silently drop failed sheets.

## Acceptance Criteria

- [x] `src/transform.py` is runnable from the repository root.
- [x] Every parse-plan sheet marked for inclusion produces at least one documented CSV or an explicit parse error entry.
- [x] Output CSVs contain the required columns and are encoded as UTF-8.
- [x] No output remains in wide format; year values are melted into `fiscal_year` / `value`.
- [x] Totals and subtotals are flagged with `is_total=True`.
- [x] Empty rows, narrative footnotes, and layout-only rows are excluded from outputs.
- [x] Output file names match the parse-plan `output_dataset` values.
- [x] Any duplicate `(program, category, fiscal_year, unit, source_sheet)` rows are either prevented or explicitly documented in parser-specific notes.

**Status: COMPLETE** — All 3 slices complete: health (38 datasets / 13,376 rows), income-security (88 / 19,961), remaining-programs (96 / 16,742). Total: 222 CSVs / 50,079 rows / 0 errors. Unit detection implemented: inline section-header scanning tracks `current_unit` per row across multi-section sheets. 9 clean unit values, 0 empty-unit rows. 15 unit tests pass.

## Dependencies

- task-02-inspect
- task-02b-parse-plan

## Test / Validation Approach

- Unit-test header normalization and melt logic with synthetic workbook fixtures.
- For each completed slice, assert every produced CSV is non-empty and contains the required columns.
- Assert `fiscal_year` values are integers in a plausible range and parse errors are surfaced explicitly.
