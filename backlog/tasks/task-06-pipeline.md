# Task: Pipeline Runner and Documentation

**ID:** task-06-pipeline  
**Phase:** Build / Closeout  
**Owner:** Lead / Scribe  
**Priority:** Medium  
**Estimated Effort:** Small (half-day)

---

## Objective

Wire all pipeline steps (download → inspect → transform → schema → verify) into a single reproducible entrypoint and write a clear top-level `README.md` so any new contributor can run the full pipeline from scratch.

## Acceptance Criteria

- [ ] `run_pipeline.py` (or `Makefile` with `make data`) exists at the repo root.
- [ ] Running `python run_pipeline.py` in a clean environment with `requirements.txt` installed executes all five steps end-to-end.
- [ ] Root `README.md` is created or updated with:
  - Project purpose (one paragraph)
  - Prerequisites (Python version, `pip install -r requirements.txt`)
  - Quick-start commands
  - Description of output files and where to find them
  - Link to `docs/schemas/README.md`
  - Data citation / attribution for CBO
- [ ] Pipeline runner accepts a `--step` argument to run a single step in isolation.
- [ ] Pipeline runner logs each step's start/end time and whether it succeeded or failed.

## Implementation Notes

- Use `subprocess` or direct Python imports to chain steps.
- A `Makefile` is an acceptable alternative to a Python runner if the team prefers it.

## Dependencies

- task-01 through task-05 must be complete.

## Test Approach

- Run `python run_pipeline.py --step download` and assert no error in a test environment (can be mocked).
- Assert `README.md` exists and contains the required sections.
