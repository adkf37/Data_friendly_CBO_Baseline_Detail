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
- `environment.yml`

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

- [x] `run_pipeline.py` exists at the repository root and is the canonical entrypoint.
- [ ] `python run_pipeline.py` runs the full workflow in order on a prepared environment. *(Human Blocked — sandbox cannot resolve `www.cbo.gov`; all non-network steps run successfully)*
- [x] `python run_pipeline.py --step <name>` works for each supported individual step. *(inspect, transform, schema, verify confirmed; download blocked on network)*
- [x] The runner logs step start/end time and success/failure status.
- [x] Root `README.md` includes project purpose, prerequisites, install steps, quick start, output locations, schema links, and CBO attribution.
- [x] Documentation matches the actual output paths and command names used by the implementation.

**Status: COMPLETE (Human Blocked on network)** — `run_pipeline.py` implemented with per-step UTC timestamps, early-stop-on-failure, and `--step <name>` dispatch. 46 tests pass. Full end-to-end run blocked only by DNS resolution failure for `www.cbo.gov` in this sandbox. Re-run `python run_pipeline.py` from a network-enabled environment to close the final AC.

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
