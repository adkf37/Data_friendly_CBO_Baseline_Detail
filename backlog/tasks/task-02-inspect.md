# Task: Inspect and Profile Excel Files

**ID:** task-02-inspect  
**Phase:** Build  
**Owner:** Data Engineer  
**Reviewers:** Lead, Tester  
**Priority:** High (defines the transform plan)  
**Estimated Effort:** Small (half-day)

---

## Objective

Profile every downloaded workbook so the team can decide which sheets should be transformed, how headers are structured, where fiscal-year columns start, and which units or notes must be preserved in downstream parsing.

## Inputs

- `data/raw/*.xlsx` from `task-01-download`
- `openpyxl` from `environment.yml`

## Outputs

- `src/inspect.py`
- `docs/inspection_report.md`

## Required Workflow

1. Open each workbook with `openpyxl` in read-only mode.
2. For every sheet, capture:
   - sheet name
   - row count and column count
   - whether merged cells are present
   - likely header row range
   - likely first data row
   - detected fiscal-year columns
   - detected unit text
   - classification: `data`, `notes`, `metadata`, or `unknown`
3. Flag sheets that appear to contain multiple logical tables or unusual layouts requiring manual mapping.
4. Write a human-readable report to `docs/inspection_report.md` summarizing workbook-by-workbook findings and open questions.

## Acceptance Criteria

- [x] `src/inspect.py` is runnable from the repository root.
- [x] Every workbook in `data/raw/` receives at least one profile entry in `docs/inspection_report.md`.
- [x] Each sheet profile records sheet dimensions, inferred header rows, fiscal-year detection, unit detection, and sheet classification.
- [x] Sheets that appear to be notes/metadata or contain multiple tables are explicitly flagged.
- [x] The report is detailed enough for a human to draft a per-sheet transform plan without reopening the workbook.
- [x] The script runs without error across all downloaded workbooks.

**Status: COMPLETE** — 230 workbooks inspected; `docs/inspection_report.md` generated (328KB, 12,280 lines). 335 sheets profiled across all workbooks.

## Dependencies

- task-01-download

## Test / Validation Approach

- Unit-test sheet enumeration and header inference with a synthetic workbook fixture.
- Assert `docs/inspection_report.md` is generated and non-empty after running against fixture workbooks.
