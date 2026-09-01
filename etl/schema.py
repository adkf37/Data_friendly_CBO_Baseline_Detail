"""Build stable row schemas, dataset descriptors, release metadata, and catalog.

The structural schema is intentionally separate from release-specific facts.
Each logical dataset has one ``schema.json``; every CSV vintage has a
``.metadata.json`` sidecar containing provenance, coverage, and superscript
annotations extracted from the corresponding source workbook.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

if sys.path:
    script_dir = Path(__file__).resolve().parent
    if Path(sys.path[0]).resolve() == script_dir:
        sys.path[0] = str(script_dir.parent)

from etl.annotations import (
    AnnotationCatalog,
    ObservationContext,
    VariableNote,
    load_annotation_catalog,
    match_variable_notes,
)
from etl.config import (
    CATALOG_PATH,
    PROCESSED_DIR,
    RAW_DIR,
    SCHEMAS_DIR,
    DatasetConfig,
    dataset_for_program_id,
    vintage_from_name,
)


SCHEMA_VERSION = "1.0.0"
JSON_SCHEMA_DRAFT = "https://json-schema.org/draft/2020-12/schema"

CORE_COLUMN_META: list[dict[str, object]] = [
    {
        "name": "program",
        "type": ["string"],
        "description": "Canonical CBO program name keyed by the stable source identifier.",
        "minLength": 1,
    },
    {
        "name": "category",
        "type": ["string"],
        "description": "Leaf line-item label from the source worksheet.",
        "minLength": 1,
    },
    {
        "name": "fiscal_year",
        "type": ["integer", "null"],
        "description": "Federal fiscal year; null for every other period type.",
        "minimum": 1900,
        "maximum": 2100,
    },
    {
        "name": "value",
        "type": ["number"],
        "description": "Parsed numeric value from the source cell.",
    },
    {
        "name": "unit",
        "type": ["string"],
        "description": "Unit of measure for value, resolved from source labels and parse metadata.",
        "minLength": 1,
    },
    {
        "name": "source_file",
        "type": ["string"],
        "description": "Original CBO workbook filename in data/raw.",
        "pattern": r"\.xlsx$",
    },
    {
        "name": "source_sheet",
        "type": ["string"],
        "description": "Worksheet name within the source workbook.",
        "minLength": 1,
    },
    {
        "name": "is_total",
        "type": ["boolean"],
        "description": "Whether the source category is an aggregate total or subtotal.",
    },
    {
        "name": "program_id",
        "type": ["string"],
        "description": "Stable numeric CBO identifier parsed from the source filename.",
        "pattern": r"^\d{5}$",
    },
    {
        "name": "category_path",
        "type": ["string"],
        "description": "Full hierarchy-aware breadcrumb ending in category.",
        "minLength": 1,
    },
    {
        "name": "period_type",
        "type": ["string"],
        "description": "Period semantics for the observation.",
        "enum": [
            "fiscal_year",
            "calendar_year",
            "award_year",
            "school_year",
            "cumulative_fiscal_years",
            "unmapped",
        ],
    },
    {
        "name": "period_start_year",
        "type": ["integer", "null"],
        "description": "First year represented by the source period.",
        "minimum": 1900,
        "maximum": 2100,
    },
    {
        "name": "period_end_year",
        "type": ["integer", "null"],
        "description": "Last year represented by the source period.",
        "minimum": 1900,
        "maximum": 2100,
    },
    {
        "name": "period_label",
        "type": ["string"],
        "description": "Normalized source period label, such as 2026 or 2026-2030.",
    },
    {
        "name": "source_row",
        "type": ["integer"],
        "description": "One-based worksheet row containing the numeric source value.",
        "minimum": 1,
    },
    {
        "name": "source_column",
        "type": ["integer"],
        "description": "One-based worksheet column containing the numeric source value.",
        "minimum": 1,
    },
]

USDA_COLUMN_META: list[dict[str, object]] = [
    {
        "name": "table_title",
        "type": ["string"],
        "description": "Top-level USDA source table heading containing the observation.",
    },
    {
        "name": "section",
        "type": ["string"],
        "description": "First intermediate USDA heading; empty when none exists.",
    },
    {
        "name": "subsection",
        "type": ["string"],
        "description": "Remaining intermediate USDA headings joined with ' / '.",
    },
]


@dataclass(frozen=True)
class ReleaseInfo:
    csv_path: Path
    dataset: DatasetConfig
    vintage: str
    row_count: int
    columns: tuple[str, ...]
    fiscal_years: tuple[int, ...]
    period_start_years: tuple[int, ...]
    period_end_years: tuple[int, ...]
    period_types: tuple[str, ...]
    source_files: tuple[str, ...]
    source_sheets: tuple[str, ...]
    units: tuple[str, ...]
    has_totals: bool
    annotation_contexts: tuple[ObservationContext, ...]


def _json_write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _typed_values(rows: list[dict[str, str]], column: str) -> tuple[int, ...]:
    values: set[int] = set()
    for row in rows:
        value = (row.get(column) or "").strip()
        if value:
            try:
                values.add(int(value))
            except ValueError:
                continue
    return tuple(sorted(values))


def _read_release(csv_path: Path) -> ReleaseInfo:
    with csv_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        columns = tuple(reader.fieldnames or ())
    if not rows:
        raise ValueError(f"Processed CSV contains no rows: {csv_path}")

    program_ids = {row.get("program_id", "").strip() for row in rows}
    program_ids.discard("")
    if len(program_ids) != 1:
        raise ValueError(f"Expected exactly one program_id in {csv_path}; found {sorted(program_ids)}")
    program_id = next(iter(program_ids))
    dataset = dataset_for_program_id(program_id)
    if dataset is None:
        raise ValueError(f"program_id {program_id!r} in {csv_path} is not registered")

    contexts: set[ObservationContext] = set()
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
            contexts.add(
                ObservationContext(
                    source_file=source_file,
                    source_sheet=source_sheet,
                    source_row=source_row,
                    source_column=source_column,
                    category_path=category_path,
                )
            )

    vintage = vintage_from_name(csv_path.name)
    if not vintage:
        source_names = {row.get("source_file", "") for row in rows}
        vintage = next((vintage_from_name(name) for name in source_names if vintage_from_name(name)), "")
    if not vintage:
        raise ValueError(f"Could not determine release vintage for {csv_path}")

    return ReleaseInfo(
        csv_path=csv_path,
        dataset=dataset,
        vintage=vintage,
        row_count=len(rows),
        columns=columns,
        fiscal_years=_typed_values(rows, "fiscal_year"),
        period_start_years=_typed_values(rows, "period_start_year"),
        period_end_years=_typed_values(rows, "period_end_year"),
        period_types=tuple(sorted({row["period_type"] for row in rows if row.get("period_type")})),
        source_files=tuple(sorted({row["source_file"] for row in rows if row.get("source_file")})),
        source_sheets=tuple(sorted({row["source_sheet"] for row in rows if row.get("source_sheet")})),
        units=tuple(sorted({row["unit"] for row in rows if row.get("unit")})),
        has_totals=any(row.get("is_total", "").lower() == "true" for row in rows),
        annotation_contexts=tuple(
            sorted(
                contexts,
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


def _field_definition(meta: dict[str, object]) -> dict[str, object]:
    field = {key: value for key, value in meta.items() if key != "name"}
    field_type = field.pop("type")
    if not isinstance(field_type, list):
        raise TypeError("Field metadata type must be a list")
    field["type"] = field_type[0] if len(field_type) == 1 else field_type
    return field


def _common_fields_schema() -> dict[str, object]:
    return {
        "$schema": JSON_SCHEMA_DRAFT,
        "title": "CBO Baseline Detail Common Field Definitions",
        "description": "Reusable definitions for processed CBO baseline-detail row fields.",
        "$defs": {
            str(meta["name"]): _field_definition(meta)
            for meta in CORE_COLUMN_META + USDA_COLUMN_META
        },
    }


def _row_schema(*, usda: bool) -> dict[str, object]:
    metadata = CORE_COLUMN_META + (USDA_COLUMN_META if usda else [])
    family = "usda_baseline_detail" if usda else "baseline_detail"
    return {
        "$schema": JSON_SCHEMA_DRAFT,
        "title": "USDA Baseline Detail Row" if usda else "CBO Baseline Detail Row",
        "description": (
            "One processed observation with explicit USDA hierarchy and cell-level provenance."
            if usda
            else "One processed observation with period semantics and cell-level provenance."
        ),
        "type": "object",
        "properties": {
            str(meta["name"]): {"$ref": f"common_fields.schema.json#/$defs/{meta['name']}"}
            for meta in metadata
        },
        "required": [str(meta["name"]) for meta in metadata],
        "additionalProperties": False,
        "x-schema-version": SCHEMA_VERSION,
    }


def _relative_path(target: Path, start: Path) -> str:
    return Path(os.path.relpath(target, start)).as_posix()


def _dataset_schema(
    dataset: DatasetConfig,
    dataset_dir: Path,
    schemas_dir: Path,
) -> dict[str, object]:
    family_schema = schemas_dir / f"{dataset.schema_family}.schema.json"
    return {
        "$schema": JSON_SCHEMA_DRAFT,
        "title": f"{dataset.title} Baseline Detail",
        "description": (
            f"Stable row contract for all {dataset.title} baseline-detail vintages. "
            "Release-specific provenance and source notes are stored in .metadata.json sidecars."
        ),
        "allOf": [
            {"$ref": _relative_path(family_schema, dataset_dir)},
            {
                "type": "object",
                "properties": {
                    "program": {"const": dataset.title},
                    "program_id": {"const": dataset.program_id},
                },
            },
        ],
        "x-cbo": {
            "dataset": dataset.key,
            "program_id": dataset.program_id,
            "source_url": dataset.source_url,
            "schema_family": dataset.schema_family,
            "schema_version": SCHEMA_VERSION,
        },
    }


def _annotation_payload(note: VariableNote) -> dict[str, object]:
    return {
        "category_path": note.category_path or None,
        "marker": note.marker,
        "variable_note": note.variable_note or None,
        "source_label": note.source_label,
        "source": {
            "file": note.source_file,
            "sheet": note.source_sheet,
            "row": note.label_row,
            "column": note.label_column,
        },
    }


def _coverage(values: tuple[int, ...]) -> dict[str, int] | None:
    return {"start_year": values[0], "end_year": values[-1]} if values else None


def _release_metadata(info: ReleaseInfo, notes: list[VariableNote]) -> dict[str, object]:
    return {
        "dataset": info.dataset.key,
        "program_id": info.dataset.program_id,
        "program": info.dataset.title,
        "vintage": info.vintage,
        "data_file": info.csv_path.name,
        "schema": "schema.json",
        "schema_version": SCHEMA_VERSION,
        "sha256": hashlib.sha256(info.csv_path.read_bytes()).hexdigest(),
        "row_count": info.row_count,
        "columns": list(info.columns),
        "fiscal_year_coverage": _coverage(info.fiscal_years),
        "period_coverage": _coverage(tuple(sorted(set(info.period_start_years + info.period_end_years)))),
        "period_types": list(info.period_types),
        "source_files": list(info.source_files),
        "source_sheets": list(info.source_sheets),
        "units": list(info.units),
        "contains_totals": info.has_totals,
        "aggregation_note": (
            "Exclude rows where is_total is true before summing across categories to avoid double-counting."
            if info.has_totals
            else None
        ),
        "annotations": [_annotation_payload(note) for note in notes],
    }


def build_catalog(
    processed_dir: Path = PROCESSED_DIR,
    catalog_path: Path = CATALOG_PATH,
) -> int:
    """Build a deterministic machine-readable catalog from dataset directories."""

    datasets: list[dict[str, object]] = []
    for schema_path in sorted(processed_dir.glob("*/schema.json")):
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        cbo = schema.get("x-cbo", {})
        releases: list[dict[str, object]] = []
        for metadata_path in sorted(schema_path.parent.glob("baseline_*.metadata.json")):
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            releases.append(
                {
                    "vintage": metadata["vintage"],
                    "data": _relative_path(schema_path.parent / metadata["data_file"], catalog_path.parent),
                    "metadata": _relative_path(metadata_path, catalog_path.parent),
                    "row_count": metadata["row_count"],
                    "period_coverage": metadata["period_coverage"],
                }
            )
        if not releases:
            continue
        datasets.append(
            {
                "dataset": cbo.get("dataset"),
                "program_id": cbo.get("program_id"),
                "title": schema.get("title"),
                "source_url": cbo.get("source_url"),
                "schema_family": cbo.get("schema_family"),
                "schema": _relative_path(schema_path, catalog_path.parent),
                "releases": sorted(releases, key=lambda item: str(item["vintage"]), reverse=True),
            }
        )
    if not datasets:
        print(f"No dataset schemas found under {processed_dir}")
        return 1
    _json_write(
        catalog_path,
        {
            "title": "CBO Baseline Projections for Selected Programs",
            "description": "Machine-readable catalog of processed baseline-detail datasets and vintages.",
            "schema_version": SCHEMA_VERSION,
            "datasets": datasets,
        },
    )
    print(f"Catalog complete. datasets={len(datasets)}, catalog={catalog_path}")
    return 0


def _render_schema_readme(
    releases_by_dataset: dict[str, list[ReleaseInfo]],
    schemas_dir: Path,
    processed_dir: Path,
) -> str:
    lines = [
        "# CBO Baseline Detail Schemas\n\n",
        "Structural schemas are stable across vintages. Each logical dataset directory contains one "
        "`schema.json`; release-specific provenance and superscript notes live in the matching "
        "`.metadata.json` sidecar.\n\n",
        "## Shared row schemas\n\n",
        "- [`baseline_detail.schema.json`](baseline_detail.schema.json): standard baseline-detail rows.\n",
        "- [`usda_baseline_detail.schema.json`](usda_baseline_detail.schema.json): standard rows plus USDA hierarchy fields.\n",
        "- [`common_fields.schema.json`](common_fields.schema.json): shared field definitions and constraints.\n\n",
        "## Dataset index\n\n",
        "| Dataset | Program ID | Schema family | Releases | Dataset schema |\n",
        "|---|---:|---|---:|---|\n",
    ]
    for dataset_key, releases in sorted(releases_by_dataset.items()):
        dataset = releases[0].dataset
        schema_path = processed_dir / dataset_key / "schema.json"
        link = _relative_path(schema_path, schemas_dir)
        lines.append(
            f"| {dataset.title} | `{dataset.program_id}` | `{dataset.schema_family}` | "
            f"{len(releases)} | [`schema.json`]({link}) |\n"
        )
    return "".join(lines)


def generate_schemas(
    processed_dir: Path = PROCESSED_DIR,
    schemas_dir: Path = SCHEMAS_DIR,
    raw_dir: Path | None = RAW_DIR,
    catalog_path: Path = CATALOG_PATH,
) -> int:
    """Generate stable schemas and release metadata for every processed CSV."""

    csv_paths = sorted(processed_dir.rglob("*.csv"))
    if not csv_paths:
        print(f"No CSV files found in {processed_dir}. Run the transform first.")
        return 1

    infos = [_read_release(path) for path in csv_paths]
    releases_by_dataset: dict[str, list[ReleaseInfo]] = defaultdict(list)
    for info in infos:
        expected_dir = processed_dir / info.dataset.key
        if info.csv_path.parent.resolve() != expected_dir.resolve():
            raise ValueError(
                f"Processed release is not in its canonical dataset directory: {info.csv_path}; "
                f"expected {expected_dir}"
            )
        releases_by_dataset[info.dataset.key].append(info)

    requested_sources: dict[str, set[str]] = {}
    for info in infos:
        for context in info.annotation_contexts:
            requested_sources.setdefault(context.source_file, set()).add(context.source_sheet)
    annotation_catalog = (
        load_annotation_catalog(raw_dir, requested_sources)
        if raw_dir is not None and raw_dir.exists()
        else AnnotationCatalog(by_source={})
    )
    notes_by_path = {
        info.csv_path: match_variable_notes(info.annotation_contexts, annotation_catalog)
        for info in infos
    }

    all_notes = [note for notes in notes_by_path.values() for note in notes]
    expected_note_identities = {
        (source_file, source_sheet, item.raw_label, item.marker, item.variable_note)
        for (source_file, source_sheet), annotations in annotation_catalog.by_source.items()
        for item in annotations
    }
    represented_note_identities = {
        (note.source_file, note.source_sheet, note.source_label, note.marker, note.variable_note)
        for note in all_notes
    }
    unresolved_markers = (
        annotation_catalog.marker_references - annotation_catalog.resolved_marker_references
    )
    unrepresented_notes = expected_note_identities - represented_note_identities
    annotation_errors = (
        unresolved_markers
        + len(unrepresented_notes)
        + len(annotation_catalog.missing_files)
        + len(annotation_catalog.missing_sheets)
    )

    schemas_dir.mkdir(parents=True, exist_ok=True)
    _json_write(schemas_dir / "common_fields.schema.json", _common_fields_schema())
    _json_write(schemas_dir / "baseline_detail.schema.json", _row_schema(usda=False))
    _json_write(schemas_dir / "usda_baseline_detail.schema.json", _row_schema(usda=True))

    for stale in processed_dir.rglob("baseline_*.metadata.json"):
        stale.unlink()
    for stale in processed_dir.glob("*/schema.json"):
        stale.unlink()
    for dataset_key, releases in releases_by_dataset.items():
        dataset = releases[0].dataset
        dataset_dir = processed_dir / dataset_key
        _json_write(dataset_dir / "schema.json", _dataset_schema(dataset, dataset_dir, schemas_dir))
        for info in releases:
            metadata_path = info.csv_path.with_suffix(".metadata.json")
            _json_write(metadata_path, _release_metadata(info, notes_by_path[info.csv_path]))

    (schemas_dir / "README.md").write_text(
        _render_schema_readme(releases_by_dataset, schemas_dir, processed_dir),
        encoding="utf-8",
    )
    catalog_rc = build_catalog(processed_dir=processed_dir, catalog_path=catalog_path)

    print(
        f"Schema generation complete. logical_datasets={len(releases_by_dataset)}, "
        f"releases={len(infos)}, variable_notes={len(all_notes)}, "
        f"resolved_markers={annotation_catalog.resolved_marker_references}/"
        f"{annotation_catalog.marker_references}, annotation_errors={annotation_errors}, "
        f"schemas_dir={schemas_dir}"
    )
    return 1 if annotation_errors or catalog_rc else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate stable dataset schemas, release metadata, and catalog.json."
    )
    parser.add_argument("--processed-dir", type=Path, default=PROCESSED_DIR)
    parser.add_argument("--schemas-dir", type=Path, default=SCHEMAS_DIR)
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--catalog", type=Path, default=CATALOG_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return generate_schemas(
        processed_dir=args.processed_dir,
        schemas_dir=args.schemas_dir,
        raw_dir=args.raw_dir,
        catalog_path=args.catalog,
    )


if __name__ == "__main__":
    raise SystemExit(main())
