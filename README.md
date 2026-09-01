# Data Friendly CBO Baseline Detail

A reproducible ETL pipeline that converts the Congressional Budget Office's
[Baseline Projections for Selected Programs](https://www.cbo.gov/data/baseline-projections-selected-programs)
Excel workbooks into versioned, machine-readable CSV datasets.

All source data is published by the Congressional Budget Office (CBO). Each
processed observation retains its source workbook, worksheet, row, and column.

## Prerequisites

- Miniconda, Anaconda, or another compatible Conda installation
- Internet access when downloading new workbooks

## Install

Create and activate the repository's Conda environment:

```bash
conda env create -f environment.yml
conda activate cbo-baseline-detail
```

To update an existing environment after `environment.yml` changes:

```bash
conda env update -f environment.yml --prune
```

Run all commands below from the repository root.

## Quick Start

Run the complete pipeline, including discovery and download from cbo.gov:

```bash
python scripts/run_pipeline.py
```

Rebuild from the workbooks already stored in `data/raw/` without accessing the
network:

```bash
python scripts/run_pipeline.py --step inspect
python scripts/run_pipeline.py --step transform
python scripts/run_pipeline.py --step schema
python scripts/run_pipeline.py --step verify
```

The pipeline stops on the first failed step. Its steps run in this order:

```text
cbo.gov -> data/raw/ -> inspection -> transformation -> schemas/metadata -> verification
              |              |              |                 |                 |
        manifest.json   inspection report   CSVs        schemas + catalog   verification report
```

## Repository Layout

```text
environment.yml                 Conda environment and Python dependencies

etl/                            Importable ETL implementation
  annotations.py                Superscript-marker and note extraction
  config.py                     Paths and logical-dataset configuration loader
  download.py                   Workbook discovery, download, and manifest creation
  inspect.py                    Raw-workbook structural inspection
  transform.py                  Workbook-to-CSV transformation
  schema.py                     Schema, metadata, annotation, and catalog generation
  validate.py                   Processed-to-source reconciliation
  datasets/usda.py              USDA-specific hierarchy adapter

scripts/                        Repository-level command entry points
  run_pipeline.py               Complete pipeline or one named pipeline step
  build_schemas.py              Rebuild schemas, metadata, and catalog
  build_catalog.py              Rebuild only catalog.json from existing artifacts
  generate_parse_plans.py       Regenerate parse plans from the inspection report

config/
  datasets.yml                  Stable registry of the 30 logical datasets
  parse_plans/*.yml             Workbook- and sheet-specific parsing instructions

data/
  raw/                          Original CBO workbooks and manifest.json
  processed/<dataset>/          Versioned CSVs, dataset schema, and release metadata

schemas/                        Shared JSON Schema row contracts and schema index
catalog.json                    Machine-readable dataset and release index
docs/                           Generated inspection and verification reports
tests/                          Unit and pipeline tests
```

`config/datasets.yml` and `config/parse_plans/*.yml` are the maintained inputs
that describe how source workbooks map to logical datasets. Processed CSVs,
metadata sidecars, shared schemas, `catalog.json`, and files in `docs/` are
generated artifacts.

## Commands

Run one pipeline step:

```bash
python scripts/run_pipeline.py --step download
python scripts/run_pipeline.py --step inspect
python scripts/run_pipeline.py --step transform
python scripts/run_pipeline.py --step schema
python scripts/run_pipeline.py --step verify
```

The underlying ETL modules can also be invoked directly when custom arguments
are needed:

```bash
python -m etl.download --help
python -m etl.inspect --help
python -m etl.transform --help
python -m etl.schema --help
python -m etl.validate --help
```

Maintenance utilities are available for narrower rebuilds:

```bash
python scripts/build_schemas.py
python scripts/build_catalog.py
python scripts/generate_parse_plans.py
```

`generate_parse_plans.py` rewrites `config/parse_plans/*.yml` from
`docs/inspection_report.md`; review those configuration changes before running
the transform.

## Processed Data

Each logical dataset has one directory, one stable dataset schema, and one CSV
plus metadata sidecar for every available release:

```text
data/processed/child_nutrition/
|-- schema.json
|-- baseline_2025-01.csv
|-- baseline_2025-01.metadata.json
|-- baseline_2026-02.csv
`-- baseline_2026-02.metadata.json
```

The standard processed row contains:

| Column | Description |
|---|---|
| `program`, `program_id` | Canonical program name and stable CBO identifier |
| `category` | Leaf source label |
| `category_path` | Complete hierarchy-aware breadcrumb |
| `fiscal_year` | Fiscal year for annual fiscal-year observations |
| `period_type` | Fiscal, calendar, award, school, cumulative, or unmapped period |
| `period_start_year`, `period_end_year`, `period_label` | Explicit period bounds and source label |
| `value`, `unit` | Parsed numeric value and source unit |
| `is_total` | Whether the row represents an aggregate total or subtotal |
| `source_file`, `source_sheet`, `source_row`, `source_column` | Exact source-cell lineage |

USDA Farm Programs releases additionally contain `table_title`, `section`, and
`subsection`. These expose the deeper USDA hierarchy as queryable columns while
retaining `category_path` as its lossless representation.

Rows where `is_total` is `true` may overlap with detailed rows. Exclude them
before summing categories unless the intended result is a source total.

## Schema and Metadata Model

Stable structure and release-specific information are kept separate:

1. [`schemas/common_fields.schema.json`](schemas/common_fields.schema.json)
   defines reusable field types and constraints.
2. [`schemas/baseline_detail.schema.json`](schemas/baseline_detail.schema.json)
   defines the standard row layout.
3. [`schemas/usda_baseline_detail.schema.json`](schemas/usda_baseline_detail.schema.json)
   extends that layout with USDA hierarchy fields.
4. Each `data/processed/<dataset>/schema.json` fixes the logical dataset's
   program identity and references the appropriate shared row schema.
5. Each release's `.metadata.json` contains its vintage, source files,
   worksheets, row count, period coverage, units, CSV hash, and annotations.

The generated [`schemas/README.md`](schemas/README.md) indexes the dataset
schemas. The root [`catalog.json`](catalog.json) indexes every logical dataset
and release for machine discovery.

## Superscript Notes

During the schema step, the raw XLSX files are opened with rich-text support so
actual superscript markers can be associated with their note definitions.
Resolved annotations are stored in the affected release's `.metadata.json`,
keyed to `category_path` and the exact source label cell.

Annotations are not embedded in the stable row schemas because their wording
and marker assignments can vary by release. Schema generation exits nonzero if
a referenced source file or sheet is unavailable, or if an annotation marker
cannot be resolved.

## Adding or Updating Releases

1. Run the download step, or place the source workbook in `data/raw/`.
2. Run the inspection step and review `docs/inspection_report.md`.
3. Add or adjust the appropriate file in `config/parse_plans/` if the workbook
   structure is new or changed.
4. Run the transform, schema, and verify steps.
5. Review `docs/verification_report.md` and the changes under `data/processed/`.

## Validation

Run the unit test suite:

```bash
python -m unittest discover -s tests -v
```

Reconcile processed observations against the cached source workbooks:

```bash
python -m etl.validate
```

Validation checks source values, coordinate completeness, duplicate lineage,
canonical program identities, units, and period semantics. Any failed target
makes the command exit nonzero and is recorded in
[`docs/verification_report.md`](docs/verification_report.md).

## Attribution

Source data: Congressional Budget Office, *Baseline Projections for Selected
Programs*. CBO remains the canonical publisher of the source workbooks.
