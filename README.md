# Data Friendly CBO Baseline Detail

This repository is building a reproducible pipeline that turns the Congressional Budget Office's baseline detail workbooks into machine-readable, tidy datasets.

## Current Status

- `task-01-download` is implemented, validated, and closed out.
- `task-02-inspect` is now implemented with `src/inspect.py`, `tests/test_inspect.py`, and `docs/inspection_report.md`.
- The next build slice after validation is `task-02b-parse-plan`.
- The full end-to-end pipeline (`run_pipeline.py`, transforms, schemas, verification) is still in progress.

## What Works Today

The current implemented entrypoint is the download step:

```bash
python -m pip install -r requirements.txt
python src/download.py --help
python src/download.py
```

Expected outputs for the current slice:

- downloaded Excel workbooks in `data/raw/`
- manifest metadata in `data/raw/manifest.json`

Inspection entrypoint:

```bash
python src/inspect.py --help
python src/inspect.py
```

Expected inspection output:

- workbook profile report in `docs/inspection_report.md`

## Validation Snapshot

- `python -m unittest discover -s tests -v` passes
- `python src/download.py --help` runs from the repository root
- mocked rerun/force checks and failure-path checks passed during Validate
- a live fetch against `www.cbo.gov` was blocked by sandbox DNS resolution and is documented in `.squad/validation_report.md`

## Planned Build Order

1. `task-02b-parse-plan`
2. `task-03-transform`
3. `task-04-schema`
4. `task-05-verify`
5. `task-06-pipeline`

See `STATUS.md`, `.squad/sprint.md`, and `.squad/review_report.md` for the latest handoff state.
