# Backlog - Data_friendly_CBO_Baseline_Detail

## Project Background

The Congressional Budget Office (CBO) publishes detailed baseline budget projections for approximately 30 selected programs. These publications are released as individual Excel (.xlsx) and PDF files. While valuable, the files are formatted for human readers — merged cells, multi-row headers, mixed units, and narrative annotations — making them difficult to use in bulk data analysis or downstream pipelines.

This project transforms those Excel files into machine-readable, tidy CSV datasets suitable for analysis, visualization, and storage in a GitHub data repository.

## Core Deliverable

A reproducible Python pipeline that:
1. Downloads all Excel files from the CBO baseline-projections page.
2. Parses and normalizes each file into one or more tidy (long-format) CSV files.
3. Produces a detailed data schema document for every CSV output.
4. Validates each output against the source Excel to verify numeric fidelity.

## Goals

- **Coverage:** All ~30 program Excel files from the CBO baseline-projections page.
- **Format:** Long/tidy CSV with consistent column names (`program`, `category`, `fiscal_year`, `value`, `unit`).
- **Schemas:** One schema file per output CSV documenting columns, types, units, and notes.
- **Verification:** Automated reconciliation checks that totals/subtotals in output match source.
- **Reproducibility:** A single command (`make data` or `python run_pipeline.py`) re-downloads and re-processes everything from scratch.

## Success Criteria

- [ ] All CBO baseline Excel files (ignoring PDFs) are downloaded to `data/raw/`.
- [ ] Each Excel file is transformed to one or more CSVs in `data/processed/`.
- [ ] Every processed CSV has a corresponding schema in `docs/schemas/`.
- [ ] A verification report confirms output totals match source for every program.
- [ ] A `README.md` at the repo root explains how to run the pipeline end-to-end.
- [ ] No hard-coded secrets; all URLs sourced from a config or discovery step.

## Out of Scope

- PDF parsing (CBO also publishes PDF versions; these are explicitly excluded).
- Forecasting or modeling on top of the data.
- Automated updates triggered by CBO publish events (future work).
