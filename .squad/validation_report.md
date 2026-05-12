# Validation Report - Data_friendly_CBO_Baseline_Detail

**Date:** 2026-05-12  
**Phase:** Validate  
**Task ID:** `task-05-verify`  
**Recommendation:** Fail — return to Build for `task-05-verify`

## Scope

Validate the latest `task-05-verify` build (`src/verify.py`, `tests/test_verify.py`, and `docs/verification_report.md`) against the verification-task acceptance criteria and the sprint commitment for the next ordered build item after schema closeout.

## Checks Run

### 1. Environment bootstrap

```bash
python -m pip install -r requirements.txt
```

- **Result:** Passed
- **Evidence:** Declared dependencies installed successfully from `requirements.txt`; no extra setup was required to run the verifier, tests, or workbook reconciliation.

### 2. Existing unit tests

```bash
python -m unittest discover -s tests -v
```

- **Result:** Passed
- **Evidence:** 24 tests passed total, including `tests/test_verify.py` coverage for pass/fail reporting, non-zero exit behavior, and `verification_include_totals` handling.

### 3. CLI runnable-from-root smoke check

```bash
python src/verify.py --help
```

- **Result:** Passed
- **Evidence:** Help output rendered successfully from the repository root with `--parse-plan`, `--input-dir`, `--processed-dir`, and `--report` options.

### 4. Real verification run

```bash
python src/verify.py
```

- **Result:** Failed
- **Evidence:** Command regenerated `docs/verification_report.md`, printed `Verification complete. targets=299, pass=24, exempt=0, non_exempt_failures=275, report=docs/verification_report.md`, and exited with status code `1`.

### 5. Parse-plan/report coverage and data-presence audit

```bash
python - <<'PY'
from pathlib import Path
import yaml

root = Path("/home/runner/work/Data_friendly_CBO_Baseline_Detail/Data_friendly_CBO_Baseline_Detail")
parse_plan = yaml.safe_load((root / "config" / "workbook_parse_plan.yaml").read_text(encoding="utf-8")) or {}
include_count = 0
for workbook in parse_plan.get("workbooks", []):
    for sheet in workbook.get("sheets", []):
        if sheet.get("include"):
            include_count += 1

raw_files = sorted((root / "data" / "raw").glob("*.xlsx"))
processed_files = sorted((root / "data" / "processed").glob("*.csv"))
empty_processed = [p.name for p in processed_files if p.stat().st_size == 0]
report = (root / "docs" / "verification_report.md").read_text(encoding="utf-8")
report_sections = report.count("## `")

print(f"raw_xlsx={len(raw_files)}")
print(f"processed_csv={len(processed_files)}")
print(f"empty_processed={len(empty_processed)}")
print(f"included_parse_targets={include_count}")
print(f"report_sections={report_sections}")
PY
```

- **Result:** Passed
- **Evidence:** Validation confirmed the repo has `raw_xlsx=230`, `processed_csv=177`, `empty_processed=0`, `included_parse_targets=299`, and `report_sections=299`, so every included parse-plan target has a corresponding verification section even though most currently fail reconciliation.

### 6. Verification failure-pattern audit

```bash
python - <<'PY'
from pathlib import Path

report = (Path("/home/runner/work/Data_friendly_CBO_Baseline_Detail/Data_friendly_CBO_Baseline_Detail") / "docs" / "verification_report.md").read_text(encoding="utf-8")
patterns = {
    "processed_csv_missing": "processed CSV missing:",
    "no_fiscal_years": "no fiscal years inferred from source",
    "sheet_missing": "sheet missing:",
    "no_year_columns": "parse plan has no year_columns",
    "no_processed_rows": "no processed rows matched source_file/source_sheet scope",
}
for label, token in patterns.items():
    print(f"{label}={report.count(token)}")
PY
```

- **Result:** Passed
- **Evidence:** The report’s failure notes are concentrated in concrete implementation gaps rather than validation setup problems: `processed_csv_missing=122`, `no_fiscal_years=120`, `sheet_missing=10`, `no_year_columns=42`, and `no_processed_rows=58`.

## Blocked Checks

- None. The required local validation checks were runnable in this sandbox using the checked-in workbooks, parse plan, processed CSVs, and verifier implementation.

## Acceptance Criteria Coverage

- [x] `src/verify.py` is runnable from the repository root
- [x] Every included parse-plan dataset has a corresponding verification result
- [x] `docs/verification_report.md` records pass/fail status and fiscal-year variance details for each dataset
- [x] The verifier uses both absolute and relative tolerances and documents any tolerated exceptions
- [x] The command exits non-zero when non-exempt verification fails
- [ ] Validate cannot be marked complete because `docs/verification_report.md` still shows `275` non-exempt failures (requirement: zero non-exempt failures)

## Remaining Risks / Follow-up

- `task-05-verify` does not yet satisfy its Validate-phase gate because the repository-scale reconciliation run still fails for most included targets.
- The failure notes point to several explicit Build follow-ups that need implementation work in the parser/parse-plan/output alignment before Validate can pass:
  - missing processed datasets for many included targets (`processed CSV missing` appears 122 times)
  - source-sheet parsing gaps where the verifier cannot infer fiscal years (`no fiscal years inferred from source` appears 120 times)
  - parse-plan incompleteness (`parse plan has no year_columns` appears 42 times)
  - workbook/sheet-name mismatches (`sheet missing` appears 10 times)
- `task-06-pipeline` should remain queued until `task-05-verify` can produce a zero-non-exempt-failure report.

## Recommendation

Return the repo to **Build** for `task-05-verify`. The validation workflow itself is runnable and reproducible, but the required repository-scale verification gate is not met: the real `python src/verify.py` run still exits non-zero and produces `275` non-exempt failures in `docs/verification_report.md`, so the task does not meet its acceptance criteria and cannot advance to Closeout yet.
