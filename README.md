# Data Friendly CBO Baseline Detail

A reproducible ETL pipeline that turns the Congressional Budget Office's
[Baseline Projections for Selected Programs](https://www.cbo.gov/data/baseline-projections-selected-programs)
Excel workbooks into versioned, machine-readable CSV datasets.

All source data is published by the Congressional Budget Office (CBO). This
repository preserves the original workbook, worksheet, row, and column for
every processed observation.

## Prerequisites

- Miniconda, Anaconda, or another compatible Conda installation
- Internet access for downloading new workbooks

## Install

```bash
conda env create -f environment.yml
conda activate cbo-baseline-detail
```

## Quick Start

Run the complete cached-data pipeline:

```bash
python scripts/run_pipeline.py --step inspect
python scripts/run_pipeline.py --step transform
python scripts/run_pipeline.py --step schema
python scripts/run_pipeline.py --step verify
```

Run every step, including the network download:

```bash
python scripts/run_pipeline.py
```

Individual ETL modules are also runnable directly:

```bash
python -m etl.download --help
python -m etl.inspect --help
python -m etl.transform --slice all
python -m etl.schema
python -m etl.validate
```

Repository-wide build utilities live in `scripts/`:

```bash
python scripts/build_schemas.py
python scripts/build_catalog.py
python scripts/generate_parse_plans.py
```

## Repository Layout

```text
etl/                         Importable download, transform, schema, and validation package
etl/datasets/                Dataset-specific adapters, including USDA hierarchy handling
scripts/                     Thin repository-level build commands
config/datasets.yml          Stable logical dataset registry
config/parse_plans/*.yml     Workbook- and sheet-specific parsing instructions
data/raw/                    Original CBO workbooks and download manifest
data/processed/<dataset>/    Versioned CSV releases, schema.json, and metadata sidecars
schemas/                     Shared JSON Schema row contracts
catalog.json                 Machine-readable dataset and release index
docs/                        Inspection and source-cell verification reports
```

## Processed Data

Each logical dataset has its own directory. Release filenames use a consistent
vintage convention:

```text
data/processed/child_nutrition/
├── schema.json
├── baseline_2025-01.csv
├── baseline_2025-01.metadata.json
├── baseline_2026-02.csv
└── baseline_2026-02.metadata.json
```

The standard processed row contains:

| Column | Description |
|---|---|
| `program`, `program_id` | Canonical program identity and stable CBO identifier |
| `category` | Leaf source label |
| `category_path` | Full hierarchy-aware breadcrumb |
| `fiscal_year` | Fiscal year for annual fiscal-year observations |
| `period_type` | Fiscal, calendar, award, school, cumulative, or unmapped period |
| `period_start_year`, `period_end_year`, `period_label` | Explicit period bounds and label |
| `value`, `unit` | Parsed numeric value and source unit |
| `is_total` | Whether the row represents an aggregate total or subtotal |
| `source_file`, `source_sheet`, `source_row`, `source_column` | Exact source-cell lineage |

USDA Farm Programs releases additionally contain `table_title`, `section`, and
`subsection`. The original `category_path` remains as the lossless hierarchy.

Rows where `is_total` is `true` may overlap with detailed rows. Exclude them
before summing across categories unless the intended result is a source total.

## Schema Model

Schemas and release metadata have separate responsibilities:

1. [`schemas/common_fields.schema.json`](schemas/common_fields.schema.json)
   defines reusable field types and constraints.
2. [`schemas/baseline_detail.schema.json`](schemas/baseline_detail.schema.json)
   and [`schemas/usda_baseline_detail.schema.json`](schemas/usda_baseline_detail.schema.json)
   define the two stable row layouts.
3. Each logical dataset directory contains one `schema.json` that fixes the
   program identity and references the appropriate shared row schema.
4. Each CSV has a `.metadata.json` sidecar containing vintage-specific source
   files, worksheets, row counts, coverage, units, hashes, and annotations.

The complete schema index is in [`schemas/README.md`](schemas/README.md), and
[`catalog.json`](catalog.json) indexes every logical dataset and release.

## Superscript Notes

The schema build opens the raw XLSX files with rich-text support and extracts
actual superscript letter markers. Resolved note text is stored in the affected
release's `.metadata.json` file, keyed to `category_path` and the exact source
label cell. Notes are not placed in the stable dataset schema because their
wording and marker assignments can change between vintages.

The schema step fails if a referenced source workbook or worksheet is missing,
a superscript marker has no definition, or a resolved source annotation is not
represented in release metadata.

## Validation

Run the complete unit test suite:

```bash
python -m unittest discover -s tests -v
```

Run source-cell reconciliation against all cached workbooks:

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
