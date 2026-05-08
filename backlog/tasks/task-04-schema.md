# Task: Write Data Schemas

**ID:** task-04-schema  
**Phase:** Build  
**Owner:** Scribe  
**Priority:** Medium  
**Estimated Effort:** Small-Medium (half-day to one day)

---

## Objective

For every processed CSV in `data/processed/`, produce a corresponding schema file in `docs/schemas/` that documents each column's name, data type, allowed values or range, unit, and any relevant notes.

## Acceptance Criteria

- [ ] Script or notebook `src/generate_schemas.py` auto-generates a draft schema from each processed CSV.
- [ ] Each schema file is saved as `docs/schemas/<csv_basename>.md`.
- [ ] Schema files include:
  - Column name
  - Data type (string, integer, float, boolean)
  - Description
  - Unit (where applicable)
  - Example values
  - Notes (e.g., "is_total=True rows are subtotals and should typically be excluded from aggregation")
- [ ] A master index `docs/schemas/README.md` lists all schema files with a one-line description of each dataset.

## Implementation Notes

- Auto-generate from `pandas` `describe()` and `dtypes` to reduce manual effort.
- Scribe agent reviews and enriches auto-generated drafts with context from the CBO source files.

## Dependencies

- task-03-transform (processed CSVs must exist)

## Test Approach

- Assert a schema file exists for every CSV in `data/processed/`.
- Assert each schema file contains the required column sections.
