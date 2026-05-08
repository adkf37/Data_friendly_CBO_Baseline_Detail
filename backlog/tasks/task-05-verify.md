# Task: Verify Transforms Against Source

**ID:** task-05-verify  
**Phase:** Build / Validate  
**Owner:** Tester  
**Priority:** High (quality gate)  
**Estimated Effort:** Medium (one day)

---

## Objective

Confirm that the numeric values in every processed CSV faithfully reproduce the values in the source Excel files. Catch rounding errors, dropped rows, mis-parsed units, and off-by-one fiscal year shifts.

## Acceptance Criteria

- [ ] Script `src/verify.py` exists and is runnable.
- [ ] For each program, the script:
  1. Reads the source Excel and sums values by fiscal year (for each data sheet).
  2. Reads the processed CSV(s) for that program and sums values by fiscal year (excluding `is_total=True` rows to avoid double-counting).
  3. Compares the two totals and flags any deviation > 0.01% as a failure.
- [ ] Verification results are written to `docs/verification_report.md` with pass/fail per program and fiscal year.
- [ ] Script exits with a non-zero code if any program has verification failures.
- [ ] Zero failures is required before the Validate phase can be marked complete.

## Implementation Notes

- Use absolute difference and relative difference thresholds for comparison.
- Log warnings (not failures) for programs where totals intentionally differ (e.g., rounding in source).
- The verification report must be human-readable enough to diagnose failures without re-running the pipeline.

## Dependencies

- task-03-transform (processed CSVs must exist)

## Test Approach

- Unit-test the comparison logic with synthetic data that has a known discrepancy.
- Integration test: run verify on real outputs and assert zero failures.
