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

# ---------------------------------------------------------------------------
# Column metadata table (fixed schema from transform.OUTPUT_COLUMNS)
# ---------------------------------------------------------------------------

COLUMN_META: list[dict] = [
    {
        "name": "program",
        "type": "string",
        "description": "CBO program name inferred from the source workbook filename.",
        "unit": "N/A",
        "notes": "Derived from the workbook filename; may include a version suffix for older files.",
    },
    {
        "name": "category",
        "type": "string",
        "description": "Line-item label as it appears in the source worksheet after header normalization.",
        "unit": "N/A",
        "notes": (
            "Rows where ``is_total`` is ``true`` represent aggregated totals or subtotals "
            "and should be excluded from sum-based aggregations to avoid double-counting."
        ),
    },
    {
        "name": "fiscal_year",
        "type": "integer",
        "description": "Federal fiscal year to which the value applies (Oct 1 – Sep 30).",
        "unit": "Year",
        "notes": (
            f"Only years in the range {2019}–{2040} are included; historical prior-year "
            "columns outside that range are silently dropped by the transform."
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
        "description": "Unit of measure for the ``value`` column, sourced from the parse plan.",
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
        "notes": "Combine with ``source_file`` for a fully qualified provenance reference.",
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
]


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
        example = sample_rows[0].get(col, "") if sample_rows else ""
        # Truncate long example values for readability
        if isinstance(example, str) and len(example) > 40:
            example = example[:37] + "..."
        lines.append(
            f"| `{col}` | {meta['type']} | {meta['description']} | {meta['unit']} | `{example}` | {meta['notes']} |\n"
        )
    return "".join(lines)


def _render_schema_doc(info: DatasetInfo) -> str:
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
        f"**Dataset:** `{info.basename}`  \n"
        f"**Vintage:** {vintage or 'see source_file'}  \n"
        f"**Rows:** {info.row_count:,}  \n"
        f"**Fiscal years covered:** {year_range}  \n"
        f"\n"
        f"## Purpose\n\n"
        f"Tidy long-form CBO baseline data for the **{program_list}** program(s), "
        f"extracted from CBO budget baseline workbooks published by the Congressional "
        f"Budget Office. Each row represents a single program/category/fiscal-year "
        f"observation.\n"
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


def _render_readme(infos: list[DatasetInfo], schemas_dir: Path) -> str:
    lines = [
        "# CBO Baseline Dataset Schemas\n\n",
        "One schema document exists for every processed CSV in `data/processed/`. "
        "Each file documents column definitions, provenance, and aggregation caveats.\n\n",
        f"**Total datasets:** {len(infos)}\n\n",
        "## Column reference (all datasets share this schema)\n\n",
        _TABLE_HEADER,
    ]
    for meta in COLUMN_META:
        lines.append(
            f"| `{meta['name']}` | {meta['type']} | {meta['description']} | {meta['unit']} | — | {meta['notes']} |\n"
        )

    lines.append("\n## Dataset index\n\n")
    lines.append("| Dataset | Rows | Fiscal years | Programs | Schema |\n")
    lines.append("|---|---|---|---|---|\n")
    for info in sorted(infos, key=lambda x: x.basename):
        year_range = (
            f"{info.fiscal_years[0]}–{info.fiscal_years[-1]}"
            if len(info.fiscal_years) > 1
            else (str(info.fiscal_years[0]) if info.fiscal_years else "—")
        )
        programs = ", ".join(info.programs[:2]) + ("…" if len(info.programs) > 2 else "")
        schema_link = f"[{info.basename}.md]({info.basename}.md)"
        lines.append(f"| `{info.basename}` | {info.row_count:,} | {year_range} | {programs} | {schema_link} |\n")

    return "".join(lines)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def generate_schemas(
    processed_dir: Path = Path("data/processed"),
    schemas_dir: Path = Path("docs/schemas"),
) -> int:
    csv_paths = sorted(processed_dir.glob("*.csv"))
    if not csv_paths:
        print(f"No CSV files found in {processed_dir}. Run the transform first.")
        return 1

    schemas_dir.mkdir(parents=True, exist_ok=True)

    infos: list[DatasetInfo] = []
    for csv_path in csv_paths:
        info = _read_dataset(csv_path)
        infos.append(info)
        schema_path = schemas_dir / f"{info.basename}.md"
        schema_path.write_text(_render_schema_doc(info), encoding="utf-8")

    readme_path = schemas_dir / "README.md"
    readme_path.write_text(_render_readme(infos, schemas_dir), encoding="utf-8")

    print(
        f"Schema generation complete. datasets={len(infos)}, "
        f"schemas_dir={schemas_dir}, index={readme_path}"
    )
    return 0


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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return generate_schemas(
        processed_dir=args.processed_dir,
        schemas_dir=args.schemas_dir,
    )


if __name__ == "__main__":
    raise SystemExit(main())
