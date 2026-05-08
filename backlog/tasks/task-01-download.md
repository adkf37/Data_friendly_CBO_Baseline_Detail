# Task: Download CBO Baseline Excel Files

**ID:** task-01-download  
**Phase:** Build  
**Owner:** Data Engineer  
**Priority:** High (blocks all other tasks)  
**Estimated Effort:** Small (half-day)

---

## Objective

Fetch all Excel (.xlsx) files from the CBO baseline-projections index page and save them locally to `data/raw/`.

## Acceptance Criteria

- [ ] Script `src/download.py` exists and is runnable.
- [ ] Script scrapes `https://www.cbo.gov/data/baseline-projections-selected-programs` for `.xlsx` links.
- [ ] All discovered Excel files are downloaded to `data/raw/<filename>.xlsx`.
- [ ] PDFs are explicitly skipped.
- [ ] Script is idempotent: re-running skips files already downloaded unless `--force` flag is passed.
- [ ] A download manifest (`data/raw/manifest.json`) is written listing filename, source URL, and download timestamp for each file.
- [ ] Script exits with a non-zero code and informative message if the CBO page is unreachable.

## Implementation Notes

- Use `requests` + `BeautifulSoup` for scraping.
- Use `pathlib.Path` for file I/O.
- Log progress to stdout with program name and file size.
- Store raw files without modification.

## Dependencies

- None (first task)

## Test Approach

- Unit-test the link-extraction logic with a saved HTML fixture.
- Integration test: run the download and assert `data/raw/` is non-empty.
