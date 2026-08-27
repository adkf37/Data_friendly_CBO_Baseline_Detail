# Data Friendly CBO Baseline Detail

A reproducible pipeline that turns the [Congressional Budget Office's](https://www.cbo.gov/) baseline detail workbooks into machine-readable, tidy CSV datasets.

> **CBO Attribution:** All source data is published by the Congressional Budget Office. Downloaded workbooks are available at <https://www.cbo.gov/data/baseline-projections-selected-programs>. The CBO grants permission to reproduce its data for non-commercial purposes with attribution.

## Project Purpose

The CBO publishes fiscal-year baseline projections for federal programs (Medicare, Medicaid, Social Security, student loans, veterans benefits, and more) as Excel workbooks. This pipeline:

1. **Downloads** the workbooks from the CBO index page.
2. **Inspects** each workbook and generates a structural profile report.
3. **Transforms** every included sheet into a tidy CSV with consistent columns.
4. **Documents** each processed dataset with a Markdown schema file, including variable notes extracted from actual superscript-formatted Excel labels.
5. **Verifies** every processed value against its exact source workbook cell and checks period, unit, and lineage semantics.

## Prerequisites

- Python 3.9 or later
- Internet access for the `download` step (subsequent steps use cached files in `data/raw/`)

## Install

```bash
python -m pip install -r requirements.txt
```

## Quick Start

Run the full end-to-end pipeline:

```bash
python run_pipeline.py
```

Run a single step:

```bash
python run_pipeline.py --step download   # download workbooks → data/raw/
python run_pipeline.py --step inspect    # profile workbooks  → docs/inspection_report.md
python run_pipeline.py --step transform  # extract CSVs       → data/processed/
python run_pipeline.py --step schema     # generate schemas   → docs/schemas/
python run_pipeline.py --step verify     # reconcile outputs  → docs/verification_report.md
```

Individual step scripts are also runnable directly:

```bash
python src/download.py --help
python src/inspect.py --help
python src/transform.py --slice all --help
python src/generate_schemas.py --help
python src/verify.py --help
```

## Output Locations

| Output | Location | Description |
|---|---|---|
| Raw workbooks | `data/raw/*.xlsx` | Downloaded CBO Excel workbooks |
| Manifest | `data/raw/manifest.json` | Download provenance metadata |
| Inspection report | `docs/inspection_report.md` | Structural profile of every workbook |
| Parse plan | `config/workbook_parse_plan.yaml` | Sheet-level instructions for the transformer |
| Processed CSVs | `data/processed/*.csv` | Tidy period-aware data, one file per source workbook/dataset |
| Parse error log | `data/processed/parse_errors.log` | Sheets that could not be parsed (see note) |
| Parse warning log | `data/processed/parse_warnings.log` | Included nonstandard sheets represented with the generic coordinate-preserving parser |
| Schema docs | `docs/schemas/*.md` | Column-level documentation and source superscript variable notes per dataset |
| Schema index | `docs/schemas/README.md` | Master index linking all schema files |
| Verification report | `docs/verification_report.md` | Source-vs-processed reconciliation results |

> **Nonstandard layouts:** Included sheets are never silently dropped. Sheets without a coordinated period header use a generic parser that preserves numeric values and exact source coordinates, records `period_type=unmapped` where needed, and adds an entry to `parse_warnings.log`. Hard failures appear in `parse_errors.log` and make the transform exit non-zero.

## Processed CSV Schema

Every file in `data/processed/` contains these columns:

| Column | Type | Description |
|---|---|---|
| `program` | string | Canonical program name, stable across workbook vintages |
| `category` | string | Leaf row label from the source worksheet (e.g. "Mandatory outlays") |
| `fiscal_year` | integer or blank | Annual federal fiscal year; blank for other period types |
| `value` | float | Value in the unit indicated by the `unit` column |
| `unit` | string | Row/section-specific unit of measurement |
| `source_file` | string | Source workbook filename |
| `source_sheet` | string | Source worksheet name within the workbook |
| `is_total` | boolean | `true` if the row appears to be a subtotal or grand total |
| `program_id` | string | Stable numeric CBO source identifier |
| `category_path` | string | Hierarchy-aware table/section/category path |
| `period_type` | string | Fiscal, calendar, award, school, cumulative fiscal, or unmapped period |
| `period_start_year` | integer or blank | First year in the period |
| `period_end_year` | integer or blank | Last year in the period |
| `period_label` | string | Normalized source period label |
| `source_row` | integer | One-based source worksheet row |
| `source_column` | integer | One-based source worksheet column |

> **`is_total` note:** Rows flagged `is_total=true` may overlap with non-total rows, causing double-counting if aggregated naïvely. Filter `is_total != 'true'` for most aggregations. See individual schema docs in `docs/schemas/` for dataset-specific guidance.

## Schema Links

Full column-level documentation for every processed dataset is in [`docs/schemas/README.md`](docs/schemas/README.md).

Each dataset schema also contains a **Variable Notes** section. The schema step opens the raw XLSX files with rich-text support, extracts only actual superscript letter markers, resolves repeated footnote alphabets within each worksheet, and binds note text to affected `category_path` values. When an annotated source label is not represented in the processed CSV, the note is retained explicitly as a source-only annotation.

## Validation

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

The schema step fails its annotation audit if a referenced workbook or worksheet is missing, a superscript marker has no note text, or a resolved annotation is absent from the generated schema. The verification step (`python run_pipeline.py --step verify`) checks exact source-cell values, coordinate completeness, duplicate lineage, canonical program identities, units, and period semantics. Former parse-plan exemptions are included and must pass; any failed target makes the pipeline exit non-zero.

## Attribution

Source data: Congressional Budget Office — *Baseline Projections for Selected Programs* (<https://www.cbo.gov/data/baseline-projections-selected-programs>). All workbooks are published by the CBO and reproduced here for non-commercial research purposes.
