# Task: Inspect and Profile Excel Files

**ID:** task-02-inspect  
**Phase:** Build  
**Owner:** Data Engineer  
**Priority:** High (informs transform design)  
**Estimated Effort:** Small (half-day)

---

## Objective

Profile every downloaded Excel file to understand its structure: sheet names, header rows, data ranges, column types, and units. Produce a human-readable profile report to guide transform logic.

## Acceptance Criteria

- [ ] Script `src/inspect.py` exists and is runnable.
- [ ] For each file in `data/raw/`, the script outputs a profile entry covering:
  - Sheet names
  - Number of rows and columns per sheet
  - Inferred header row(s)
  - Fiscal year columns detected
  - Unit annotations found (e.g., "billions of dollars", "millions of people")
- [ ] Profile is saved to `docs/inspection_report.md` (markdown table or structured prose).
- [ ] Script runs without error on all downloaded files.

## Implementation Notes

- Use `openpyxl` to read files without executing macros.
- Handle merged cells gracefully (read the top-left value).
- Flag any sheets that appear to be metadata or notes pages (e.g., sheet named "Notes" or "Sources").

## Dependencies

- task-01-download (raw files must be present)

## Test Approach

- Unit-test sheet-name extraction with a small synthetic Excel fixture.
- Assert inspection report is non-empty after running on `data/raw/`.
