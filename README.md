# Data Friendly CBO Baseline Detail

This repository is building a reproducible pipeline that turns the Congressional Budget Office's baseline detail workbooks into machine-readable, tidy datasets.

## Current Status

- `task-01-download` is implemented, validated, and closed out.
- `task-02-inspect` and `task-02b-parse-plan` are implemented and complete.
- `task-03-transform` health slice is implemented, validated, and closed out with `src/transform.py` plus `tests/test_transform.py`.
- `task-03-transform` income-security slice is implemented, validated, and closed out; `src/transform.py --slice income-security` now writes 72 audited datasets while surfacing 37 explicit parse errors for follow-up.
- The next ordered build target is the remaining-programs slice of `task-03-transform`.
- The full end-to-end pipeline (`run_pipeline.py`, transforms, schemas, verification) is still in progress.

## What Works Today

Implemented entrypoints today:

```bash
python -m pip install -r requirements.txt
python src/download.py --help
python src/inspect.py --help
python src/transform.py --help
```

Expected current outputs:

- downloaded Excel workbooks in `data/raw/`
- manifest metadata in `data/raw/manifest.json`
- workbook profile report in `docs/inspection_report.md`
- machine-readable parse plan in `config/workbook_parse_plan.yaml`
- health-slice CSV outputs in `data/processed/`
- income-security slice outputs via `python src/transform.py --slice income-security --output-dir /tmp/cbo_closeout_income`
- explicit transform failures in `data/processed/parse_errors.log`

## Validation Snapshot

- `python -m unittest discover -s tests -v` passes
- `python src/download.py --help` runs from the repository root
- `python src/inspect.py --help` runs from the repository root
- `python src/transform.py --help` runs from the repository root
- the validated health-slice transform writes 38 non-empty CSVs with required headers and `implausible_year_rows=0`
- the closed-out income-security slice writes 72 non-empty CSVs with required headers, `missing_entries=0`, `datasets_with_duplicates=0`, and `implausible_year_rows=0`
- the income-security slice still surfaces 37 explicit parse errors, preserved as follow-up parser work in `parse_errors.log`
- the real health-slice transform still logs 14 explicit parse errors, preserved as follow-up risk in `.squad/validation_report.md`

## Planned Build Order

1. `task-03-transform` — remaining programs slice
2. `task-04-schema`
3. `task-05-verify`
4. `task-06-pipeline`

See `STATUS.md`, `.squad/sprint.md`, and `.squad/review_report.md` for the latest handoff state.
