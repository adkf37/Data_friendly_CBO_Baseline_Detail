# Validation Report - Data_friendly_CBO_Baseline_Detail

**Date:** 2026-05-11  
**Phase:** Validate  
**Task ID:** `task-04-schema`  
**Recommendation:** Pass — advance to Closeout for `task-04-schema`

## Scope

Validate the latest `task-04-schema` build (`src/generate_schemas.py`, `docs/schemas/`, and `tests/test_generate_schemas.py`) against the schema-task acceptance criteria and the sprint commitment for the next ordered build item after transform closeout.

## Checks Run

### 1. Environment bootstrap

```bash
python -m pip install -r requirements.txt
```

- **Result:** Passed
- **Evidence:** Declared dependencies installed successfully, including `openpyxl` and `PyYAML`, and no extra setup was required beyond `requirements.txt`.

### 2. Existing unit tests

```bash
python -m unittest discover -s tests -v
```

- **Result:** Passed
- **Evidence:** 22 tests passed total, including the schema-generator coverage, README index, provenance, and `is_total` guidance checks in `tests/test_generate_schemas.py`.

### 3. CLI runnable-from-root smoke check

```bash
python src/generate_schemas.py --help
```

- **Result:** Passed
- **Evidence:** Help output rendered successfully from the repository root with `--processed-dir` and `--schemas-dir` options.

### 4. Real schema-generation run

```bash
python src/generate_schemas.py --schemas-dir /tmp/cbo_schema_validate
```

- **Result:** Passed
- **Evidence:** Command completed successfully and reported `Schema generation complete. datasets=177, schemas_dir=/tmp/cbo_schema_validate, index=/tmp/cbo_schema_validate/README.md`.

### 5. Schema coverage and required-section audit

```bash
python - <<'PY'
from pathlib import Path
import csv

root = Path("/home/runner/work/Data_friendly_CBO_Baseline_Detail/Data_friendly_CBO_Baseline_Detail")
processed = root / "data" / "processed"
schemas = Path("/tmp/cbo_schema_validate")
processed_names = sorted(p.stem for p in processed.glob("*.csv"))
schema_names = sorted(p.stem for p in schemas.glob("*.md") if p.name != "README.md")
missing_schemas = sorted(set(processed_names) - set(schema_names))
extra_schemas = sorted(set(schema_names) - set(processed_names))
required_sections = ["## Purpose", "## Provenance", "## Columns", "## is_total Interpretation"]
missing_sections = []
missing_column_details = []
missing_is_total_guidance = []
missing_provenance_values = []
required_columns = ["program", "category", "fiscal_year", "value", "unit", "source_file", "source_sheet", "is_total"]

for csv_path in sorted(processed.glob("*.csv")):
    schema_path = schemas / f"{csv_path.stem}.md"
    content = schema_path.read_text(encoding="utf-8")
    for section in required_sections:
        if section not in content:
            missing_sections.append((csv_path.stem, section))
    for column in required_columns:
        if f"`{column}`" not in content:
            missing_column_details.append((csv_path.stem, column))
    if "double-counting" not in content:
        missing_is_total_guidance.append(csv_path.stem)
    with csv_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        first_row = next(reader, None)
    if first_row:
        if first_row["source_file"] not in content or first_row["source_sheet"] not in content:
            missing_provenance_values.append(csv_path.stem)

readme = (schemas / "README.md").read_text(encoding="utf-8")
missing_readme_links = [name for name in processed_names if f"[{name}.md]({name}.md)" not in readme]

print(f"processed_csvs={len(processed_names)}")
print(f"schema_docs={len(schema_names)}")
print(f"missing_schemas={len(missing_schemas)}")
print(f"extra_schemas={len(extra_schemas)}")
print(f"missing_sections={len(missing_sections)}")
print(f"missing_column_details={len(missing_column_details)}")
print(f"missing_is_total_guidance={len(missing_is_total_guidance)}")
print(f"missing_provenance_values={len(missing_provenance_values)}")
print(f"missing_readme_links={len(missing_readme_links)}")
PY
```

- **Result:** Passed
- **Evidence:**  
  - The generator preserved a strict 1:1 mapping between processed CSVs and schema docs (`processed_csvs=177`, `schema_docs=177`, `missing_schemas=0`, `extra_schemas=0`).  
  - Every generated schema contained the required sections and all output-column details (`missing_sections=0`, `missing_column_details=0`).  
  - Every generated schema documented `is_total` double-counting guidance and included real provenance values from the CSVs (`missing_is_total_guidance=0`, `missing_provenance_values=0`).  
  - The generated `docs/schemas/README.md` equivalent linked every dataset schema (`missing_readme_links=0`).

### 6. Reproducibility drift check against checked-in schema docs

```bash
diff -rq docs/schemas /tmp/cbo_schema_validate
```

- **Result:** Passed
- **Evidence:** No output from `diff -rq`, so the checked-in `docs/schemas/` tree matches a fresh run of the current schema generator exactly.

## Blocked Checks

- None. The required local validation checks were runnable in this sandbox using the checked-in processed CSVs.

## Acceptance Criteria Coverage

- [x] Every CSV in `data/processed/` has a matching schema file in `docs/schemas/`
- [x] Each schema file documents column name, data type, description, unit applicability, example values, and notes
- [x] `docs/schemas/README.md` lists every dataset and links to its schema file
- [x] Schema file names match CSV basenames exactly
- [x] Schema docs explain how `is_total=True` rows should be interpreted for downstream analysis

## Remaining Risks / Follow-up

- The generator and checked-in schema docs are currently aligned, but Closeout should preserve that the project still has downstream backlog work in `task-05-verify` and `task-06-pipeline`.
- Existing transform parse errors remain documented in `data/processed/parse_errors.log`; they do not block schema closeout, but they remain relevant context for later verification work.

## Recommendation

Advance the repo to **Closeout** for `task-04-schema`. The schema generator is runnable from the repo root, the full unittest suite passes, a real generation run produces complete 1:1 schema coverage for all 177 processed CSVs, each schema includes the required provenance and `is_total` guidance, and the checked-in schema docs are reproducible from the current implementation.
