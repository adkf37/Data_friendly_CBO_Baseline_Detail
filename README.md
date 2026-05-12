# Data Friendly CBO Baseline Detail

A reproducible pipeline that turns the [Congressional Budget Office's](https://www.cbo.gov/) baseline detail workbooks into machine-readable, tidy CSV datasets.

> **CBO Attribution:** All source data is published by the Congressional Budget Office. Downloaded workbooks are available at <https://www.cbo.gov/data/baseline-projections-selected-programs>. The CBO grants permission to reproduce its data for non-commercial purposes with attribution.

## Project Purpose

The CBO publishes fiscal-year baseline projections for federal programs (Medicare, Medicaid, Social Security, student loans, veterans benefits, and more) as Excel workbooks. This pipeline:

1. **Downloads** the workbooks from the CBO index page.
2. **Inspects** each workbook and generates a structural profile report.
3. **Transforms** every included sheet into a tidy CSV with consistent columns.
4. **Documents** each processed dataset with a Markdown schema file.
5. **Verifies** that processed CSV totals match source workbook values within tolerance.

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
| Processed CSVs | `data/processed/*.csv` | Tidy fiscal-year data, one file per dataset |
| Parse error log | `data/processed/parse_errors.log` | Sheets that could not be parsed (see note) |
| Schema docs | `docs/schemas/*.md` | Column-level documentation per dataset |
| Schema index | `docs/schemas/README.md` | Master index linking all schema files |
| Verification report | `docs/verification_report.md` | Source-vs-processed reconciliation results |

> **Parse errors:** Some workbooks have non-standard layouts (merged cells, rotated headers, or no detectable fiscal-year columns) that prevent automatic parsing. These are logged in `parse_errors.log` and left for manual follow-up rather than silently dropped.

## Processed CSV Schema

Every file in `data/processed/` contains these columns:

| Column | Type | Description |
|---|---|---|
| `program` | string | Program name inferred from the source workbook filename |
| `category` | string | Row label from the source worksheet (e.g. "Mandatory outlays") |
| `fiscal_year` | integer | Federal fiscal year (October 1 – September 30) |
| `value` | float | Value in the unit indicated by the `unit` column |
| `unit` | string | Unit of measurement (e.g. "Millions of dollars, by fiscal year") |
| `source_file` | string | Source workbook filename |
| `source_sheet` | string | Source worksheet name within the workbook |
| `is_total` | boolean | `true` if the row appears to be a subtotal or grand total |

> **`is_total` note:** Rows flagged `is_total=true` may overlap with non-total rows, causing double-counting if aggregated naïvely. Filter `is_total != 'true'` for most aggregations. See individual schema docs in `docs/schemas/` for dataset-specific guidance.

## Schema Links

Full column-level documentation for every processed dataset is in [`docs/schemas/README.md`](docs/schemas/README.md).

## Validation

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

The verification step (`python run_pipeline.py --step verify`) reconciles all processed CSVs against their source workbooks and writes `docs/verification_report.md`. The pipeline exits non-zero if any non-exempt comparison fails.

## Attribution

Source data: Congressional Budget Office — *Baseline Projections for Selected Programs* (<https://www.cbo.gov/data/baseline-projections-selected-programs>). All workbooks are published by the CBO and reproduced here for non-commercial research purposes.
