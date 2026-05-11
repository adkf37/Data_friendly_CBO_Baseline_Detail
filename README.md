# Data Friendly CBO Baseline Detail

This repository is building a reproducible pipeline that turns the Congressional Budget Office's baseline detail workbooks into machine-readable, tidy datasets.

## Current Status

- `task-01-download` is implemented, validated, and closed out.
- `task-02-inspect` and `task-02b-parse-plan` are implemented and complete.
- `task-03-transform` is implemented, validated, and closed out across the health, income-security, and remaining-programs slices.
- `task-04-schema` is implemented, validated, and closed out with reproducible docs for all processed CSVs.
- The transform CLI now supports `--slice health`, `--slice income-security`, `--slice remaining-programs`, and `--slice all`.
- The next ordered build target is `task-05-verify`.
- The full end-to-end pipeline (`run_pipeline.py`, transforms, schemas, verification) is still in progress.

## What Works Today

Implemented entrypoints today:

```bash
python -m pip install -r requirements.txt
python src/download.py --help
python src/inspect.py --help
python src/transform.py --help
python src/generate_schemas.py --help
```

Expected current outputs:

- downloaded Excel workbooks in `data/raw/`
- manifest metadata in `data/raw/manifest.json`
- workbook profile report in `docs/inspection_report.md`
- machine-readable parse plan in `config/workbook_parse_plan.yaml`
- transform CSV outputs in `data/processed/` or a caller-supplied `--output-dir`
- schema docs in `docs/schemas/` with an index at `docs/schemas/README.md`
- validated remaining-programs outputs via `python src/transform.py --slice remaining-programs --output-dir /tmp/cbo_closeout_remaining`
- explicit transform failures in `data/processed/parse_errors.log`

## Validation Snapshot

- `python -m unittest discover -s tests -v` passes
- `python src/download.py --help` runs from the repository root
- `python src/inspect.py --help` runs from the repository root
- `python src/transform.py --help` runs from the repository root
- `python src/generate_schemas.py --help` runs from the repository root
- the closed-out health slice writes 38 non-empty CSVs with required headers and `implausible_year_rows=0`
- the closed-out income-security slice writes 72 non-empty CSVs with required headers, `missing_entries=0`, `datasets_with_duplicates=0`, and `implausible_year_rows=0`
- the closed-out remaining-programs slice writes 73 non-empty CSVs with required headers, `missing_entries=0`, `datasets_with_duplicates=0`, and `implausible_year_rows=0`
- the closed-out schema task maintains a 1:1 mapping between 177 processed CSVs and 177 schema docs with reproducible checked-in output
- real transform runs still surface explicit parse errors for follow-up (14 health, 37 income-security, 39 remaining-programs), but each included parse-plan sheet is accounted for by either CSV output or logged parse error

## Planned Build Order

1. `task-05-verify`
2. `task-06-pipeline`

See `STATUS.md`, `.squad/sprint.md`, and `.squad/review_report.md` for the latest handoff state.
