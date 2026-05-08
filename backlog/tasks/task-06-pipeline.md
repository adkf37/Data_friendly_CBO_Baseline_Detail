# Task: Pipeline Runner and Documentation

**ID:** task-06-pipeline  
**Phase:** Build / Closeout  
**Owner:** Data Engineer  
**Reviewers:** Tester, Scribe, Lead  
**Priority:** Medium  
**Estimated Effort:** Small (half-day)

---

## Objective

Provide one reproducible entrypoint for the entire workflow and a root-level README that explains how to run, validate, and interpret the pipeline outputs.

## Inputs

- Completed implementations from tasks 01-05
- `requirements.txt`

## Outputs

- Root-level `run_pipeline.py` or `Makefile`
- Root-level `README.md`

## Required Workflow

1. Choose and document one canonical entrypoint: `python run_pipeline.py`.
2. Support step-level execution for:
   - `download`
   - `inspect`
   - `transform`
   - `schema`
   - `verify`
3. Log start/end status for each invoked step and stop on the first failure.
4. Document prerequisites, setup, execution, outputs, and attribution in `README.md`.
5. Have Scribe perform the final documentation pass before closeout.

## Acceptance Criteria

- [ ] `run_pipeline.py` exists at the repository root and is the canonical entrypoint.
- [ ] `python run_pipeline.py` runs the full workflow in order on a prepared environment.
- [ ] `python run_pipeline.py --step <name>` works for each supported individual step.
- [ ] The runner logs step start/end time and success/failure status.
- [ ] Root `README.md` includes project purpose, prerequisites, install steps, quick start, output locations, schema links, and CBO attribution.
- [ ] Documentation matches the actual output paths and command names used by the implementation.

## Dependencies

- task-01-download
- task-02-inspect
- task-02b-parse-plan
- task-03-transform
- task-04-schema
- task-05-verify

## Test / Validation Approach

- Run `python run_pipeline.py --step download` in a mocked or fixture-backed environment.
- Assert `README.md` exists and contains the required sections and canonical command.
