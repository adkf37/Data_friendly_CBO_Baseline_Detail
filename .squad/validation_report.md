# Validation Report - Data_friendly_CBO_Baseline_Detail

**Date:** 2026-05-12  
**Phase:** Validate  
**Task ID:** `task-06-pipeline`  
**Recommendation:** Blocked — set `Next Action: Human Blocked`

## Scope

Validate the latest `task-06-pipeline` build (`run_pipeline.py`, `README.md`, and the repo-level generated artifacts) against the pipeline-task acceptance criteria and the Validate-phase checks in `backlog/phases.md`.

## Checks Run

### 1. Environment bootstrap

```bash
python -m pip install -r requirements.txt
```

- **Result:** Passed
- **Evidence:** The declared dependencies installed successfully in this fresh sandbox; no undeclared packages were needed to run the test suite or the pipeline steps.

### 2. Existing automated tests

```bash
python -m unittest discover -s tests -v
```

- **Result:** Passed
- **Evidence:** All `46` unit tests passed, including the task-06 pipeline runner tests in `tests/test_pipeline.py` plus the existing download / inspect / transform / schema / verify coverage.

### 3. Pipeline CLI help

```bash
python run_pipeline.py --help
```

- **Result:** Passed
- **Evidence:** Help output rendered from the repository root and documented the canonical command plus all supported named steps: `download`, `inspect`, `transform`, `schema`, and `verify`.

### 4. Step-level smoke checks

```bash
python run_pipeline.py --step download
python run_pipeline.py --step inspect
python run_pipeline.py --step transform
python run_pipeline.py --step schema
python run_pipeline.py --step verify
```

- **Result:** Partially passed / partially blocked
- **Evidence:**
  - `download` reached the live CBO fetch, then stopped immediately on sandbox DNS resolution failure for `www.cbo.gov`.
  - `inspect` passed and reported `Inspected 230 workbook(s). report=docs/inspection_report.md`.
  - `transform` passed and reported `Transform complete. slice=all, datasets=222, rows=50079, errors=0`.
  - `schema` passed and reported `Schema generation complete. datasets=222, schemas_dir=docs/schemas, index=docs/schemas/README.md`.
  - `verify` passed and reported `Verification complete. targets=299, pass=277, exempt=22, non_exempt_failures=0, report=docs/verification_report.md`.

### 5. Full pipeline smoke check

```bash
python run_pipeline.py
```

- **Result:** Blocked
- **Evidence:** The runner started in the documented order but stopped on the first step because the sandbox could not resolve `www.cbo.gov` for the live `download` step. No local runner bug was observed before the environment-level network failure.

### 6. Data integrity and coverage audit

```bash
python - <<'PY'
from pathlib import Path

root = Path(".")
raw = sorted((root / "data" / "raw").glob("*.xlsx"))
processed = sorted((root / "data" / "processed").glob("*.csv"))
processed_names = {p.stem for p in processed}
schema_names = {
    p.stem for p in (root / "docs" / "schemas").glob("*.md")
    if p.name != "README.md"
}
empty_processed = [p.name for p in processed if p.stat().st_size == 0]

print(f"raw_xlsx={len(raw)}")
print(f"processed_csv={len(processed)}")
print(f"empty_processed={len(empty_processed)}")
print(f"schema_docs={len(schema_names)}")
print(f"missing_schemas={len(processed_names - schema_names)}")
print(f"extra_schemas={len(schema_names - processed_names)}")
PY
```

- **Result:** Passed
- **Evidence:** The checked-in repo currently has `raw_xlsx=230`, `processed_csv=222`, `empty_processed=0`, `schema_docs=222`, `missing_schemas=0`, and `extra_schemas=0`.

### 7. Verification report audit

```bash
python - <<'PY'
from pathlib import Path

report = (Path("docs") / "verification_report.md").read_text(encoding="utf-8")
for token in [
    "- Pass: 277",
    "- Exempt failures: 22",
    "- Non-exempt failures: 0",
    "## Target Status",
]:
    print(f"{token} -> {token in report}")
PY
```

- **Result:** Passed
- **Evidence:** `docs/verification_report.md` contains the expected summary and confirms the repository-scale verification gate is now satisfied: `277` PASS, `22` EXEMPT, `0` non-exempt FAIL.

## Blocked Checks

- `python run_pipeline.py --step download` is blocked in this sandbox because outbound DNS resolution for `https://www.cbo.gov/data/baseline-projections-selected-programs` fails before the step can complete.
- `python run_pipeline.py` is blocked for the same reason: the runner correctly stops on first failure, and the first step is the network-dependent `download` stage.

## Acceptance Criteria Coverage

- [x] `run_pipeline.py` exists at the repository root and is the canonical entrypoint
- [ ] `python run_pipeline.py` runs the full workflow in order on a prepared environment — blocked here by sandbox DNS/network access to `www.cbo.gov`
- [x] `python run_pipeline.py --step <name>` works for `inspect`, `transform`, `schema`, and `verify`; `download` dispatch reaches the intended implementation but is externally blocked by network resolution
- [x] The runner logs step start/end time and success/failure status
- [x] Root `README.md` includes project purpose, prerequisites, install steps, quick start, output locations, schema links, and CBO attribution
- [x] Documentation matches the actual output paths and command names used by the implementation
- [x] Validate-phase artifact checks passed locally: raw workbooks are present, processed CSVs are non-empty, schema coverage is 1:1, and verification shows zero non-exempt failures

## Remaining Risks / Follow-up

- The only unresolved validation gap is a live network-enabled rerun of the `download` step and the full end-to-end pipeline command.
- `STATUS.md` previously listed stale artifact counts (`177` processed CSVs / schemas); validation refreshed the handoff artifacts to match the reproducible current state (`222` processed CSVs / schemas).
- No local evidence suggests a logic error in `run_pipeline.py`; the blocked checks are environmental rather than code failures.

## Recommendation

Set `Next Action: Human Blocked`. The repo now passes all non-network-dependent Validate checks for `task-06-pipeline`: dependencies install cleanly, all `46` tests pass, the runner help output is correct, `inspect` / `transform` / `schema` / `verify` succeed from the repo root, the generated artifacts are internally consistent (`230` raw workbooks, `222` processed CSVs, `222` schema docs), and verification reports `277` PASS / `22` EXEMPT / `0` non-exempt FAIL. The remaining gap is an environment-level one: a person must rerun `python run_pipeline.py --step download` and `python run_pipeline.py` from a network-enabled environment that can resolve and reach `www.cbo.gov`.
