# Validation Report - Data_friendly_CBO_Baseline_Detail

**Date:** 2026-05-11  
**Phase:** Validate  
**Task ID:** `task-03-transform`  
**Recommendation:** Fail — return to Build for `task-03-transform`

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
- **Evidence:** 8 tests passed total, including the new transform regression that verifies top-header year preference and duplicate-key suppression.

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

- **Result:** Failed
- **Evidence:** Command exited with status 1 after `Transform complete. slice=health, datasets=38, rows=8371, errors=14`.
- **Parse-error sample:**  
  - `51293-2020-01-childnutrition.xlsx	CNP	no fiscal years inferred`
  - `51298-2019-05-Health-Insurance.xlsx	Table 4-1	year_columns missing`
  - `54946-2021-07-dodmedicare.xlsx	DoD-MERHCF_07-2021	no fiscal years inferred`

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
        if year < 2019 or year > 2037:
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

- **Result:** Failed
- **Evidence:**  
  - All 71 included health-sheet parse-plan entries were accounted for by either an output CSV or an explicit parse-error entry (`missing_entries=0`), so no sheet was silently dropped.  
  - 38 datasets were written and all were non-empty with the required UTF-8 headers (`empty_csvs=0`, `bad_headers=0`).  
  - Duplicate `(program, category, fiscal_year, unit, source_sheet)` keys were eliminated (`datasets_with_duplicates=0`), so the latest build fixed that part of the prior validation failure.  
  - Generated output still includes 98 implausible fiscal-year rows concentrated in four 2019-05 datasets:
    - `child_nutrition_2019_05.csv` — 42 rows with years `2012`-`2018`
    - `chip_2019_05.csv` — 12 rows with year `2018`
    - `medicaid_2019_05.csv` — 8 rows with year `2018`
    - `medicare_2019_05.csv` — 36 rows with year `2018`
  - Example bad row from `/tmp/cbo_transform_validate/child_nutrition_2019_05.csv`: `category=Paid`, `fiscal_year=2012`, `source_sheet=CNP May 2019`. This keeps the slice outside the task’s “plausible fiscal year” validation expectation.

## Blocked Checks

- None. The required local validation checks were runnable in this sandbox using the checked-in raw workbooks.

## Acceptance Criteria Coverage

- [x] `src/transform.py` is runnable from the repository root
- [x] Every parse-plan sheet marked for inclusion produces at least one documented CSV or an explicit parse error entry
- [x] Output CSVs are written as UTF-8 and contain the required columns
- [x] Output rows are melted into `fiscal_year` / `value` columns rather than remaining in wide format
- [x] Totals and subtotals are flagged with `is_total=true`
- [ ] Empty rows, narrative footnotes, and layout-only rows are excluded from outputs for the affected 2019-05 health datasets
- [x] Output file names match parse-plan `output_dataset` values for the successful datasets
- [x] Duplicate `(program, category, fiscal_year, unit, source_sheet)` rows are prevented
- [ ] Fiscal-year inference is reliable for the full health slice

## Recommendation

Return the repo to **Build** for `task-03-transform`. The health-slice implementation is runnable, fully unit-tested, and no longer emits duplicate keys, but it is not ready to advance because a real health run still produces 14 explicit parse errors and 98 implausible fiscal-year rows in four 2019-05 datasets. The next build step should focus on correcting header/year inference for those 2019-05 health workbooks and then rerun Validate on the same real-slice checks.
