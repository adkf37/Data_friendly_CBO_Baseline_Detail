# Task: Create Workbook Parse Plan

**ID:** task-02b-parse-plan  
**Phase:** Build  
**Owner:** Lead  
**Reviewers:** Data Engineer, Tester  
**Priority:** High (required handoff between inspection and transform)  
**Estimated Effort:** Small (half-day)

---

## Objective

Convert inspection findings into a machine-readable workbook parse plan that tells the transform and verification steps exactly how each workbook and sheet should be handled.

## Inputs

- `docs/inspection_report.md` from `task-02-inspect`
- Architectural guidance from `.squad/decisions.md`

## Outputs

- `config/workbook_parse_plan.yaml`

## Required Workflow

1. Review the inspection report and identify every workbook/sheet that should be transformed, skipped, or split into multiple outputs.
2. Create one parse-plan entry per candidate sheet with:
   - `workbook`
   - `sheet`
   - `classification`
   - `include`
   - `output_dataset`
   - `header_rows`
   - `first_data_row`
   - `year_column_strategy`
   - `unit`
   - `notes`
   - `verification_target`
3. Mark sheets requiring custom parsing logic with an explicit override note.
4. Record any unresolved structural risks in `.squad/decisions.md` before build continues.

## Acceptance Criteria

- [ ] `config/workbook_parse_plan.yaml` exists and is valid YAML.
- [ ] Every workbook listed in `docs/inspection_report.md` has corresponding parse-plan entries for each sheet.
- [ ] Every sheet is explicitly marked as included, skipped, or split.
- [ ] Every included or split sheet has an `output_dataset` and verification target.
- [ ] Custom-parser cases are called out explicitly so transform work can be sequenced deliberately.
- [ ] No workbook proceeds to transform without a parse-plan entry.

## Dependencies

- task-02-inspect

## Test / Validation Approach

- Validate YAML syntax and required keys.
- Cross-check workbook/sheet counts against `docs/inspection_report.md`.
