# Validation Report - Data_friendly_CBO_Baseline_Detail

**Date:** 2026-05-11  
**Phase:** Validate  
**Task ID:** `task-03-transform`  
**Recommendation:** Pass — advance to Closeout for `task-03-transform`

## Scope

Validate the latest `task-03-transform` health-slice build (`src/transform.py` and `tests/test_transform.py`) against the transform acceptance criteria and the sprint commitment for the first ordered transform slice.

## Checks Run

### 1. Environment bootstrap

```bash
python -m pip install -r requirements.txt
```

- **Result:** Passed
- **Evidence:** Declared dependencies installed successfully, including `openpyxl` and `PyYAML` required by the transform workflow.

### 2. Existing unit tests

```bash
python -m unittest discover -s tests -v
```

- **Result:** Passed
- **Evidence:** 9 tests passed total, including transform regressions for plausible-year filtering, header-year preference, and duplicate-key suppression.

### 3. CLI runnable-from-root smoke check

```bash
python src/transform.py --help
```

- **Result:** Passed
- **Evidence:** Help output rendered successfully from the repository root with `--parse-plan`, `--input-dir`, `--output-dir`, and `--slice` options.

### 4. Real health-slice transform run

```bash
python src/transform.py --slice health --output-dir /tmp/cbo_transform_validate
```

- **Result:** Passed with explicit parse-error logging
- **Evidence:** Command reported `Transform complete. slice=health, datasets=38, rows=8273, errors=14` and exited non-zero because parse errors are surfaced by design.
- **Parse-error sample:**  
  - `51293-2020-01-childnutrition.xlsx	CNP	no fiscal years inferred`
  - `51293-2020-03-childnutrition.xlsx	CNP	no fiscal years inferred`
  - `51298-2019-05-Health-Insurance.xlsx	Table 4-1	year_columns missing`

### 5. Health-slice coverage and output integrity review

```bash
python - <<'PY'
from pathlib import Path
import csv
import yaml
from collections import Counter

root = Path("/home/runner/work/Data_friendly_CBO_Baseline_Detail/Data_friendly_CBO_Baseline_Detail")
out = Path("/tmp/cbo_transform_validate")
payload = yaml.safe_load((root / "config/workbook_parse_plan.yaml").read_text(encoding="utf-8")) or {}
health_keywords = ("health", "medicare", "medicaid", "chip", "nutrition")
plans = []
for workbook in payload.get("workbooks", []):
    for sheet in workbook.get("sheets", []):
        dataset = str(sheet.get("output_dataset", ""))
        if sheet.get("include") and any(keyword in dataset.lower() for keyword in health_keywords):
            plans.append((workbook["workbook"], sheet["sheet"], dataset))

error_lines = [line for line in (out / "parse_errors.log").read_text(encoding="utf-8").splitlines() if line.strip()]
error_keys = {(line.split("\t")[0], line.split("\t")[1]) for line in error_lines}
missing = []
required = ["program", "category", "fiscal_year", "value", "unit", "source_file", "source_sheet", "is_total"]
duplicates = []
implausible_years = []
empty_csvs = []
bad_headers = []

for workbook, sheet, dataset in plans:
    csv_path = out / f"{dataset}.csv"
    if not csv_path.exists() and (workbook, sheet) not in error_keys:
        missing.append((workbook, sheet, dataset))

for csv_path in sorted(out.glob("*.csv")):
    with csv_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    if fieldnames != required:
        bad_headers.append((csv_path.name, fieldnames))
    if not rows:
        empty_csvs.append(csv_path.name)
    seen = Counter()
    for row in rows:
        key = (row["program"], row["category"], row["fiscal_year"], row["unit"], row["source_sheet"])
        seen[key] += 1
        year = int(row["fiscal_year"])
        if year < 2019 or year > 2040:
            implausible_years.append((csv_path.name, row))
    dup_keys = [key for key, count in seen.items() if count > 1]
    if dup_keys:
        duplicates.append((csv_path.name, len(dup_keys)))

print(f"health_plan_entries={len(plans)}")
print(f"datasets_written={len(list(out.glob('*.csv')))}")
print(f"parse_errors={len(error_lines)}")
print(f"missing_entries={len(missing)}")
print(f"empty_csvs={len(empty_csvs)}")
print(f"bad_headers={len(bad_headers)}")
print(f"datasets_with_duplicates={len(duplicates)}")
print(f"implausible_year_rows={len(implausible_years)}")
PY
```

- **Result:** Passed
- **Evidence:**  
  - All 71 included health-sheet parse-plan entries were accounted for by either an output CSV or an explicit parse-error entry (`missing_entries=0`), so no sheet was silently dropped.  
  - 38 datasets were written and all were non-empty with the required UTF-8 headers (`empty_csvs=0`, `bad_headers=0`).  
  - Duplicate `(program, category, fiscal_year, unit, source_sheet)` keys were eliminated (`datasets_with_duplicates=0`).  
  - Implausible fiscal-year rows were fully eliminated (`implausible_year_rows=0`), resolving the prior validation failure on the four 2019-05 health datasets.

## Blocked Checks

- None. The required local validation checks were runnable in this sandbox using the checked-in raw workbooks.

## Acceptance Criteria Coverage

- [x] `src/transform.py` is runnable from the repository root
- [x] Every parse-plan sheet marked for inclusion produces at least one documented CSV or an explicit parse error entry
- [x] Output CSVs are written as UTF-8 and contain the required columns
- [x] Output rows are melted into `fiscal_year` / `value` columns rather than remaining in wide format
- [x] Totals and subtotals are flagged with `is_total=true`
- [x] Empty rows, narrative footnotes, and layout-only rows are excluded from outputs for the validated health datasets
- [x] Output file names match the parse-plan `output_dataset` values for the successful datasets
- [x] Duplicate `(program, category, fiscal_year, unit, source_sheet)` rows are prevented
- [x] Fiscal-year inference is reliable for the validated health slice

## Remaining Risks / Follow-up

- The real health-slice run still surfaces 14 explicit parse errors. That does not violate this slice’s acceptance criteria because those sheets are documented in `parse_errors.log`, but Closeout should preserve them as known follow-up work for later transform coverage improvements.

## Recommendation

Advance the repo to **Closeout** for `task-03-transform`. The health-slice implementation is runnable from the repo root, the full unittest suite passes, the real slice writes valid non-empty CSVs for all successful datasets, every included sheet is accounted for, duplicate keys are prevented, and the prior implausible-year defect is resolved.
