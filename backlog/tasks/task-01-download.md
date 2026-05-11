# Task: Download CBO Baseline Excel Files

**ID:** task-01-download  
**Phase:** Build  
**Owner:** Data Engineer  
**Reviewers:** Tester  
**Priority:** High (blocks all downstream work)  
**Estimated Effort:** Small (half-day)

---

## Objective

Discover every Excel workbook linked from the CBO baseline projections index page, download each workbook into `data/raw/`, and capture a machine-readable manifest for reproducible downstream processing.

## Inputs

- Source page: `https://www.cbo.gov/data/baseline-projections-selected-programs`
- Runtime dependencies from `requirements.txt`
- Optional CLI flags: `--force`, `--timeout`, `--retries`

## Outputs

- `src/download.py`
- `data/raw/*.xlsx` (runtime outputs; not committed)
- `data/raw/manifest.json`

## Required Workflow

1. Request the CBO index page with an explicit timeout and retry policy.
2. Parse HTML links and keep only `.xlsx` targets; ignore `.pdf` and non-file links.
3. Normalize each discovered workbook name to a stable local filename derived from the source filename.
4. Download missing workbooks to `data/raw/`; skip existing files unless `--force` is supplied.
5. Write `data/raw/manifest.json` containing one record per workbook with:
   - `program_slug`
   - `filename`
   - `source_url`
   - `discovered_at`
   - `downloaded_at`
   - `sha256`
   - `bytes`
6. Emit stdout logs for discovery count, each download/skip action, and final totals.

## Acceptance Criteria

- [x] `src/download.py` is runnable from the repository root.
- [x] The script scrapes `https://www.cbo.gov/data/baseline-projections-selected-programs` for `.xlsx` links only.
- [x] Every discovered workbook is saved to `data/raw/<source_filename>.xlsx`.
- [x] PDF links are explicitly ignored and never written to disk.
- [x] Re-running without `--force` leaves existing workbooks untouched and reports them as skipped.
- [x] Re-running with `--force` refreshes existing workbooks and rewrites manifest metadata.
- [x] `data/raw/manifest.json` is valid JSON and includes the required fields for every downloaded workbook.
- [x] The script exits non-zero with an informative error if the index page is unreachable or returns no Excel links.

**Status: COMPLETE** — 230 of 244 historical xlsx workbooks downloaded via Wayback Machine (`scripts/bulk_download.py`). 14 Feb-2026 files unavailable (not yet archived). `data/raw/manifest.json` written with sha256, bytes, source_url, timestamps.

## Dependencies

- None (first build slice)

## Test / Validation Approach

- Unit-test link extraction with a saved HTML fixture containing Excel and PDF links.
- Unit-test manifest generation with mocked downloads.
- Integration-test a mocked run that writes at least one workbook and a manifest entry under `data/raw/`.
