# Task: Verify Transforms Against Source

**ID:** task-05-verify  
**Phase:** Build / Validate  
**Owner:** Data Engineer + Tester  
**Reviewers:** Lead  
**Priority:** High (quality gate)  
**Estimated Effort:** Medium (one day)

---

## Objective

Confirm that processed CSV values faithfully reproduce the source workbook values for each included dataset, surfacing dropped rows, shifted fiscal years, unit mistakes, and double-counting before validate/closeout can pass.

## Inputs

- `data/raw/*.xlsx`
- `data/processed/*.csv`
- `config/workbook_parse_plan.yaml`

## Outputs

- `src/verify.py`
- `docs/verification_report.md`

## Required Workflow

1. For each included parse-plan target, load the relevant source workbook/sheet values and compute comparison totals by fiscal year.
2. Load the matching processed CSV rows and compute equivalent totals, excluding `is_total=True` rows unless the parse plan explicitly says otherwise.
3. Compare source and processed totals using both:
   - absolute tolerance suitable for the source unit
   - relative tolerance of `0.01%`
4. Write a human-readable report with pass/fail status, variances, and notes for any tolerated exceptions.
5. Exit non-zero if any non-exempt comparison fails.

## Acceptance Criteria

- [x] `src/verify.py` is runnable from the repository root.
- [x] Every included parse-plan dataset has a corresponding verification result.
- [x] `docs/verification_report.md` records pass/fail status and fiscal-year variance details for each dataset.
- [x] The verifier uses both absolute and relative tolerances and documents any tolerated exceptions.
- [x] The command exits non-zero when any non-exempt verification fails.
- [x] Validate cannot be marked complete until this report shows zero non-exempt failures.

**Status: COMPLETE** — `docs/verification_report.md` shows 299 targets: 277 PASS / 22 EXEMPT / 0 non-exempt FAIL. Verifier uses unit-aware absolute tolerance and 0.01% relative tolerance; all exemptions documented. Exits non-zero on any non-exempt failure.

## Dependencies

- task-03-transform
- task-02b-parse-plan

## Test / Validation Approach

- Unit-test comparison logic with synthetic data containing one passing and one failing case.
- Integration-test the verifier against cached or fixture outputs and assert zero non-exempt failures.
