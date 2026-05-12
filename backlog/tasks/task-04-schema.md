# Task: Write Data Schemas

**ID:** task-04-schema  
**Phase:** Build  
**Owner:** Data Engineer  
**Reviewers:** Scribe  
**Priority:** Medium  
**Estimated Effort:** Small-Medium (half-day to one day)

---

## Objective

Generate one schema document per processed dataset so contributors can understand the structure, units, provenance, and aggregation caveats of every CSV output without reverse-engineering the transform code.

## Inputs

- `data/processed/*.csv`
- Output naming from `config/workbook_parse_plan.yaml`
- Any parser notes recorded in `.squad/decisions.md`

## Outputs

- `src/generate_schemas.py` (or `src/schema.py`)
- `docs/schemas/<csv_basename>.md`
- `docs/schemas/README.md`

## Required Workflow

1. Enumerate every CSV in `data/processed/`.
2. Generate a draft schema document for each CSV including:
   - dataset purpose
   - source workbook/sheet provenance
   - column table with type, description, unit, example, and notes
   - any known caveats such as `is_total=True` handling
3. Build a master index file at `docs/schemas/README.md`.
4. Hand schema drafts to Scribe for prose cleanup and consistency review before the task is considered done.

## Acceptance Criteria

- [x] Every CSV in `data/processed/` has a matching schema file in `docs/schemas/`.
- [x] Each schema file documents column name, data type, description, unit applicability, example values, and notes.
- [x] `docs/schemas/README.md` lists every dataset and links to its schema file.
- [x] Schema file names match CSV basenames exactly.
- [x] Schema docs explain how `is_total=True` rows should be interpreted for downstream analysis.

**Status: COMPLETE** — `src/generate_schemas.py` generates 222 schema docs (1:1 with processed CSVs) plus `docs/schemas/README.md` index. Each schema includes provenance, column table with unit/example/notes, and `is_total` aggregation caveat. Regenerated after unit normalization fix to reflect accurate unit lists per dataset.

## Dependencies

- task-03-transform

## Test / Validation Approach

- Assert there is a 1:1 mapping between processed CSVs and schema files.
- Assert each schema file contains the required sections and a provenance note.
