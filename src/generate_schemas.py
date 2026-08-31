from __future__ import annotations

"""Generate schema documentation for processed CBO baseline datasets.

Usage
-----
python src/generate_schemas.py [--processed-dir data/processed] [--schemas-dir docs/schemas]

For each CSV in ``processed_dir`` this script writes a Markdown schema file to
``schemas_dir/<csv_basename>.md`` and updates the master index at
``schemas_dir/README.md``.
"""

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import NamedTuple

if sys.path:
    script_dir = Path(__file__).resolve().parent
    if Path(sys.path[0]).resolve() == script_dir:
        sys.path[0] = str(script_dir.parent)

from src.source_annotations import (
    AnnotationCatalog,
    ObservationContext,
    VariableNote,
    load_annotation_catalog,
    match_variable_notes,
)

# ---------------------------------------------------------------------------
# Column metadata tables. USDA datasets add hierarchy columns while all other
# datasets retain the core transform schema.
# ---------------------------------------------------------------------------

CORE_COLUMN_META: list[dict] = [
    {
        "name": "program",
        "type": "string",
        "description": "Canonical CBO program name keyed by the stable source identifier.",
        "unit": "N/A",
        "notes": "Stable across workbook vintages; use ``program_id`` as the machine key.",
    },
    {
        "name": "category",
        "type": "string",
        "description": "Leaf line-item label from the source worksheet.",
        "unit": "N/A",
        "notes": (
            "Rows where ``is_total`` is ``true`` represent aggregated totals or subtotals "
            "and should be excluded from sum-based aggregations to avoid double-counting."
        ),
    },
    {
        "name": "fiscal_year",
        "type": "integer or null",
        "description": "Annual federal fiscal year; blank for every other period type.",
        "unit": "Year",
        "notes": (
            "Historical actuals are retained. Consult ``period_type`` and the explicit "
            "period bounds before interpreting a row as annual fiscal-year data."
        ),
    },
    {
        "name": "value",
        "type": "float",
        "description": "Parsed numeric value from the source cell.",
        "unit": "See ``unit`` column",
        "notes": (
            "Negative values indicate outflows or reductions. Values originally enclosed "
            "in parentheses (e.g. ``(123)``) are converted to negative floats."
        ),
    },
    {
        "name": "unit",
        "type": "string",
        "description": "Unit of measure for ``value``, resolved from row/section labels and parse metadata.",
        "unit": "N/A",
        "notes": "Common values include 'Millions of dollars', 'Billions of dollars', and 'Thousands'.",
    },
    {
        "name": "source_file",
        "type": "string",
        "description": "Original CBO workbook filename from ``data/raw/``.",
        "unit": "N/A",
        "notes": "Use this column to trace any row back to its exact source workbook.",
    },
    {
        "name": "source_sheet",
        "type": "string",
        "description": "Worksheet name within the source workbook.",
        "unit": "N/A",
        "notes": "Combine with source file, row, and column for exact cell provenance.",
    },
    {
        "name": "is_total",
        "type": "boolean",
        "description": (
            "``true`` if the category label contains the word 'total' or 'subtotal', "
            "indicating an aggregated row."
        ),
        "unit": "N/A",
        "notes": (
            "**Always filter ``is_total = true`` rows out before computing sums or averages** "
            "across categories to avoid double-counting. Retain them for headline/summary views."
        ),
    },
    {
        "name": "program_id",
        "type": "string",
        "description": "Stable numeric CBO identifier from the source filename.",
        "unit": "N/A",
        "notes": "Preferred program join key across vintages.",
    },
    {
        "name": "category_path",
        "type": "string",
        "description": "Hierarchy-aware path from table/section headings to the leaf category.",
        "unit": "N/A",
        "notes": "Use this field instead of ``category`` when labels repeat in different subprograms.",
    },
    {
        "name": "period_type",
        "type": "string",
        "description": "Period semantics for the observation.",
        "unit": "N/A",
        "notes": "Values include fiscal_year, calendar_year, award_year, school_year, cumulative_fiscal_years, and unmapped.",
    },
    {
        "name": "period_start_year",
        "type": "integer or null",
        "description": "First year represented by the source period.",
        "unit": "Year",
        "notes": "Equals period_end_year for annual rows and is blank when the source period is not identified.",
    },
    {
        "name": "period_end_year",
        "type": "integer or null",
        "description": "Last year represented by the source period.",
        "unit": "Year",
        "notes": "For annual fiscal-year rows this equals ``fiscal_year``.",
    },
    {
        "name": "period_label",
        "type": "string",
        "description": "Normalized source period label such as 2025 or 2025-2029.",
        "unit": "N/A",
        "notes": "Rows with unrecognized periods are labeled explicitly rather than assigned a guessed year.",
    },
    {
        "name": "source_row",
        "type": "integer",
        "description": "One-based worksheet row containing the numeric source value.",
        "unit": "N/A",
        "notes": "Together with ``source_column`` identifies the exact source cell.",
    },
    {
        "name": "source_column",
        "type": "integer",
        "description": "One-based worksheet column containing the numeric source value.",
        "unit": "N/A",
        "notes": "Together with ``source_row`` identifies the exact source cell.",
    },
]

USDA_COLUMN_META: list[dict] = [
    {
        "name": "table_title",
        "type": "string",
        "description": "Top-level USDA source table heading containing the observation.",
        "unit": "N/A",
        "notes": "USDA-only. This is the first component of ``category_path``.",
    },
    {
        "name": "section",
        "type": "string or null",
        "description": "First intermediate USDA heading between the table title and leaf category.",
        "unit": "N/A",
        "notes": "USDA-only. Blank when the source hierarchy has no intermediate heading.",
    },
    {
        "name": "subsection",
        "type": "string or null",
        "description": "Second and any deeper intermediate USDA headings before the leaf category.",
        "unit": "N/A",
        "notes": (
            "USDA-only. Additional intermediate levels are retained here using "
            "the same `` / `` delimiter as ``category_path``."
        ),
    },
]

COLUMN_META = CORE_COLUMN_META + USDA_COLUMN_META


# ---------------------------------------------------------------------------
# Dataset-level metadata helpers
# ---------------------------------------------------------------------------


class DatasetInfo(NamedTuple):
    basename: str
    row_count: int
    fiscal_years: list[int]
    programs: list[str]
    source_files: list[str]
    source_sheets: list[str]
    units: list[str]
    sample_rows: list[dict]
    has_totals: bool
    annotation_contexts: tuple[ObservationContext, ...]


def _read_dataset(csv_path: Path, sample_size: int = 3) -> DatasetInfo:
    rows: list[dict] = []
    with csv_path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows.append(row)

    fiscal_years = sorted({int(r["fiscal_year"]) for r in rows if r.get("fiscal_year")})
    programs = sorted({r["program"] for r in rows if r.get("program")})
    source_files = sorted({r["source_file"] for r in rows if r.get("source_file")})
    source_sheets = sorted({r["source_sheet"] for r in rows if r.get("source_sheet")})
    units = sorted({r["unit"] for r in rows if r.get("unit")})
    has_totals = any(r.get("is_total", "false").lower() == "true" for r in rows)
    sample_rows = rows[:sample_size]
    annotation_contexts: set[ObservationContext] = set()
    for row in rows:
        try:
            source_row = int(row.get("source_row", ""))
            source_column = int(row.get("source_column", ""))
        except (TypeError, ValueError):
            continue
        source_file = (row.get("source_file") or "").strip()
        source_sheet = (row.get("source_sheet") or "").strip()
        category_path = (row.get("category_path") or "").strip()
        if source_file and source_sheet and source_row > 0 and source_column > 0 and category_path:
            annotation_contexts.add(
                ObservationContext(
                    source_file=source_file,
                    source_sheet=source_sheet,
                    source_row=source_row,
                    source_column=source_column,
                    category_path=category_path,
                )
            )

    return DatasetInfo(
        basename=csv_path.stem,
        row_count=len(rows),
        fiscal_years=fiscal_years,
        programs=programs,
        source_files=source_files,
        source_sheets=source_sheets,
        units=units,
        sample_rows=sample_rows,
        has_totals=has_totals,
        annotation_contexts=tuple(
            sorted(
                annotation_contexts,
                key=lambda item: (
                    item.source_file,
                    item.source_sheet,
                    item.source_row,
                    item.source_column,
                    item.category_path,
                ),
            )
        ),
    )


def _dataset_title(basename: str) -> str:
    """Convert a dataset basename like 'snap_2024_06' to a human title."""
    return " ".join(part.upper() if len(part) <= 4 else part.title() for part in basename.split("_"))


def _vintage_from_basename(basename: str) -> str:
    """Extract a vintage string like '2024-06' from a basename like 'snap_2024_06'."""
    match = re.search(r"(\d{4})_(\d{2})$", basename)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return ""


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

_TABLE_HEADER = "| Column | Type | Description | Unit | Example | Notes |\n|---|---|---|---|---|---|\n"


def _render_column_table(sample_rows: list[dict]) -> str:
    lines = [_TABLE_HEADER]
    for meta in COLUMN_META:
        col = meta["name"]
        if sample_rows and col not in sample_rows[0]:
            continue
        example = sample_rows[0].get(col, "") if sample_rows else ""
        # Truncate long example values for readability
        if isinstance(example, str) and len(example) > 40:
            example = example[:37] + "..."
        lines.append(
            f"| `{col}` | {meta['type']} | {meta['description']} | {meta['unit']} | `{example}` | {meta['notes']} |\n"
        )
    return "".join(lines)


def _markdown_cell(value: object) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")


def _render_variable_notes(variable_notes: list[VariableNote]) -> str:
    introduction = (
        "Superscript letter markers are read from the source workbook's actual Excel "
        "rich-text formatting. Each extracted note is attached to every affected "
        "`category_path`; a note on a parent heading therefore applies to its child rows. "
        "A source-only entry is retained when the annotated source label has no emitted "
        "row in the processed dataset.\n\n"
    )
    if not variable_notes:
        return introduction + "No superscript variable notes are attached to this dataset.\n"

    lines = [
        introduction,
        "| Affected category path | Marker | `variable_note` | Source label | Source cell |\n",
        "|---|---|---|---|---|\n",
    ]
    for note in variable_notes:
        note_text = note.variable_note or "Note text was not found in the source worksheet."
        category_path = note.category_path or "*Source label is not represented in processed rows.*"
        source = (
            f"`{_markdown_cell(note.source_file)}` / "
            f"`{_markdown_cell(note.source_sheet)}` / "
            f"R{note.label_row}C{note.label_column}"
        )
        lines.append(
            f"| {_markdown_cell(category_path)} | `{note.marker}` | "
            f"{_markdown_cell(note_text)} | {_markdown_cell(note.source_label)} | {source} |\n"
        )
    return "".join(lines)


def _render_schema_doc(info: DatasetInfo, variable_notes: list[VariableNote] | None = None) -> str:
    variable_notes = variable_notes or []
    title = _dataset_title(info.basename)
    vintage = _vintage_from_basename(info.basename)
    program_list = ", ".join(info.programs) if info.programs else "N/A"
    source_files_list = ", ".join(f"`{f}`" for f in info.source_files) if info.source_files else "N/A"
    source_sheets_list = ", ".join(f"`{s}`" for s in info.source_sheets) if info.source_sheets else "N/A"
    units_list = ", ".join(info.units) if info.units else "N/A"
    year_range = (
        f"{info.fiscal_years[0]}–{info.fiscal_years[-1]}"
        if len(info.fiscal_years) > 1
        else (str(info.fiscal_years[0]) if info.fiscal_years else "N/A")
    )

    totals_note = (
        "\n> **Aggregation caveat:** This dataset contains rows where `is_total = true`. "
        "These rows represent summary totals or subtotals drawn directly from the source "
        "worksheet. **Exclude `is_total = true` rows before summing across categories** "
        "to avoid double-counting.\n"
        if info.has_totals
        else ""
    )

    return (
        f"# Schema: {title}\n\n"
        f"- **Dataset:** `{info.basename}`\n"
        f"- **Vintage:** {vintage or 'see source_file'}\n"
        f"- **Rows:** {info.row_count:,}\n"
        f"- **Fiscal years covered:** {year_range}\n"
        f"\n"
        f"## Purpose\n\n"
        f"Tidy long-form CBO baseline data for the **{program_list}** program(s), "
        f"extracted from CBO budget baseline workbooks published by the Congressional "
        f"Budget Office. Each row represents one numeric source cell with explicit "
        f"program, category hierarchy, period semantics, and cell-level provenance.\n"
        f"{totals_note}\n"
        f"## Provenance\n\n"
        f"| Field | Value |\n"
        f"|---|---|\n"
        f"| Source file(s) | {source_files_list} |\n"
        f"| Source sheet(s) | {source_sheets_list} |\n"
        f"| Unit(s) | {units_list} |\n"
        f"\n"
        f"## Columns\n\n"
        f"{_render_column_table(info.sample_rows)}\n"
        f"## Variable Notes\n\n"
        f"{_render_variable_notes(variable_notes)}\n"
        f"## is_total Interpretation\n\n"
        f"The `is_total` column flags rows whose `category` label contains the word "
        f"'total' or 'subtotal'. These rows summarise multiple line items and must be "
        f"treated carefully in downstream analysis:\n\n"
        f"- **Summary views:** Include `is_total = true` rows to display headline figures.\n"
        f"- **Detailed aggregations:** Exclude `is_total = true` rows to prevent "
        f"double-counting when summing across categories.\n"
        f"- **Time-series analysis:** Either filter is consistent as long as it is applied "
        f"uniformly across all fiscal years being compared.\n"
    )


def _render_readme(
    infos: list[DatasetInfo],
    schemas_dir: Path,
    variable_notes_by_dataset: dict[str, list[VariableNote]] | None = None,
) -> str:
    variable_notes_by_dataset = variable_notes_by_dataset or {}
    datasets_with_notes = sum(bool(variable_notes_by_dataset.get(info.basename)) for info in infos)
    variable_note_count = sum(len(notes) for notes in variable_notes_by_dataset.values())
    source_only_count = sum(
        1
        for notes in variable_notes_by_dataset.values()
        for note in notes
        if not note.category_path
    )
    lines = [
        "# CBO Baseline Dataset Schemas\n\n",
        "One schema document exists for every processed CSV in `data/processed/`. "
        "Each file documents column definitions, provenance, and aggregation caveats.\n\n",
        f"**Total datasets:** {len(infos)}\n\n",
        "## Core column reference\n\n",
        "Every processed dataset contains these columns.\n\n",
        _TABLE_HEADER,
    ]
    for meta in CORE_COLUMN_META:
        lines.append(
            f"| `{meta['name']}` | {meta['type']} | {meta['description']} | {meta['unit']} | — | {meta['notes']} |\n"
        )

    lines.extend(
        [
            "\n## USDA-specific hierarchy columns\n\n",
            "USDA Farm Programs datasets add the following columns while retaining "
            "`category` as the leaf label and `category_path` as the full breadcrumb.\n\n",
            _TABLE_HEADER,
        ]
    )
    for meta in USDA_COLUMN_META:
        lines.append(
            f"| `{meta['name']}` | {meta['type']} | {meta['description']} | {meta['unit']} | — | {meta['notes']} |\n"
        )

    lines.extend(
        [
            "\n## Superscript variable notes\n\n",
            "Each dataset schema includes a **Variable Notes** section. Notes are extracted "
            "only from actual superscript-formatted letter markers in the source XLSX and "
            "are bound to the affected `category_path`, including inherited parent-heading notes. "
            "Source-only entries are retained when an annotated source label is not emitted in "
            "the processed CSV.\n\n",
            f"**Datasets with variable notes:** {datasets_with_notes}\n\n",
            f"**Variable-note mappings:** {variable_note_count:,}\n\n",
            f"**Source-only annotations:** {source_only_count:,}\n",
        ]
    )

    lines.append("\n## Dataset index\n\n")
    lines.append("| Dataset | Rows | Fiscal years | Programs | Variable notes | Schema |\n")
    lines.append("|---|---|---|---|---|---|\n")
    for info in sorted(infos, key=lambda x: x.basename):
        year_range = (
            f"{info.fiscal_years[0]}–{info.fiscal_years[-1]}"
            if len(info.fiscal_years) > 1
            else (str(info.fiscal_years[0]) if info.fiscal_years else "—")
        )
        programs = ", ".join(info.programs[:2]) + ("…" if len(info.programs) > 2 else "")
        note_count = len(variable_notes_by_dataset.get(info.basename, []))
        schema_link = f"[{info.basename}.md]({info.basename}.md)"
        lines.append(
            f"| `{info.basename}` | {info.row_count:,} | {year_range} | {programs} | "
            f"{note_count:,} | {schema_link} |\n"
        )

    return "".join(lines)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def generate_schemas(
    processed_dir: Path = Path("data/processed"),
    schemas_dir: Path = Path("docs/schemas"),
    raw_dir: Path | None = None,
) -> int:
    csv_paths = sorted(processed_dir.glob("*.csv"))
    if not csv_paths:
        print(f"No CSV files found in {processed_dir}. Run the transform first.")
        return 1

    schemas_dir.mkdir(parents=True, exist_ok=True)

    infos = [_read_dataset(csv_path) for csv_path in csv_paths]
    requested_sources: dict[str, set[str]] = {}
    for info in infos:
        for context in info.annotation_contexts:
            requested_sources.setdefault(context.source_file, set()).add(context.source_sheet)
    effective_raw_dir = raw_dir if raw_dir is not None else processed_dir.parent / "raw"
    catalog = (
        load_annotation_catalog(effective_raw_dir, requested_sources)
        if effective_raw_dir.exists()
        else AnnotationCatalog(by_source={})
    )
    variable_notes_by_dataset = {
        info.basename: match_variable_notes(info.annotation_contexts, catalog)
        for info in infos
    }
    all_variable_notes = [
        note
        for variable_notes in variable_notes_by_dataset.values()
        for note in variable_notes
    ]
    expected_note_identities = {
        (source_file, source_sheet, item.raw_label, item.marker, item.variable_note)
        for (source_file, source_sheet), annotations in catalog.by_source.items()
        for item in annotations
    }
    represented_note_identities = {
        (
            note.source_file,
            note.source_sheet,
            note.source_label,
            note.marker,
            note.variable_note,
        )
        for note in all_variable_notes
    }
    unresolved_markers = catalog.marker_references - catalog.resolved_marker_references
    unrepresented_notes = expected_note_identities - represented_note_identities
    annotation_errors = (
        unresolved_markers
        + len(unrepresented_notes)
        + len(catalog.missing_files)
        + len(catalog.missing_sheets)
    )

    for info in infos:
        schema_path = schemas_dir / f"{info.basename}.md"
        schema_path.write_text(
            _render_schema_doc(info, variable_notes_by_dataset[info.basename]),
            encoding="utf-8",
        )

    readme_path = schemas_dir / "README.md"
    readme_path.write_text(
        _render_readme(infos, schemas_dir, variable_notes_by_dataset),
        encoding="utf-8",
    )

    print(
        f"Schema generation complete. datasets={len(infos)}, "
        f"variable_notes={sum(len(notes) for notes in variable_notes_by_dataset.values())}, "
        f"resolved_markers={catalog.resolved_marker_references}/{catalog.marker_references}, "
        f"annotation_errors={annotation_errors}, "
        f"missing_files={len(catalog.missing_files)}, missing_sheets={len(catalog.missing_sheets)}, "
        f"schemas_dir={schemas_dir}, index={readme_path}"
    )
    return 1 if annotation_errors else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Markdown schema files for every processed CBO baseline CSV."
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=Path("data/processed"),
        help="Directory containing processed CSV files (default: data/processed)",
    )
    parser.add_argument(
        "--schemas-dir",
        type=Path,
        default=Path("docs/schemas"),
        help="Output directory for schema Markdown files (default: docs/schemas)",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory containing source XLSX workbooks (default: data/raw)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return generate_schemas(
        processed_dir=args.processed_dir,
        schemas_dir=args.schemas_dir,
        raw_dir=args.raw_dir,
    )


if __name__ == "__main__":
    raise SystemExit(main())
