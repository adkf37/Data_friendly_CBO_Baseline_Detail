"""Repository paths and dataset registry helpers.

``etl.config`` is the Python-facing configuration API.  The curated dataset
metadata lives in ``config/datasets.yml`` and the workbook-specific parsing
instructions live in ``config/parse_plans/``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / "config"
DATASETS_FILE = CONFIG_DIR / "datasets.yml"
PARSE_PLANS_DIR = CONFIG_DIR / "parse_plans"
RAW_DIR = REPO_ROOT / "data" / "raw"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
SCHEMAS_DIR = REPO_ROOT / "schemas"
CATALOG_PATH = REPO_ROOT / "catalog.json"


@dataclass(frozen=True)
class DatasetConfig:
    """Stable metadata for one logical CBO baseline-detail dataset."""

    key: str
    program_id: str
    title: str
    source_url: str
    schema_family: str = "baseline_detail"


@lru_cache(maxsize=None)
def load_datasets(path: Path = DATASETS_FILE) -> dict[str, DatasetConfig]:
    """Load and validate the logical dataset registry."""

    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = payload.get("datasets", {})
    if not isinstance(entries, dict):
        raise ValueError(f"Expected a 'datasets' mapping in {path}")

    datasets: dict[str, DatasetConfig] = {}
    program_ids: set[str] = set()
    for key, entry in entries.items():
        if not isinstance(entry, dict):
            raise ValueError(f"Dataset {key!r} in {path} must be a mapping")
        program_id = str(entry.get("program_id", "")).strip()
        title = str(entry.get("title", "")).strip()
        source_url = str(entry.get("source_url", "")).strip()
        schema_family = str(entry.get("schema_family", "baseline_detail")).strip()
        if not program_id or not title or not source_url:
            raise ValueError(f"Dataset {key!r} is missing program_id, title, or source_url")
        if program_id in program_ids:
            raise ValueError(f"Duplicate program_id {program_id!r} in {path}")
        program_ids.add(program_id)
        datasets[key] = DatasetConfig(
            key=key,
            program_id=program_id,
            title=title,
            source_url=source_url,
            schema_family=schema_family,
        )
    return datasets


DATASETS = load_datasets()
DATASETS_BY_PROGRAM_ID = {dataset.program_id: dataset for dataset in DATASETS.values()}


def dataset_for_program_id(program_id: str) -> DatasetConfig | None:
    return DATASETS_BY_PROGRAM_ID.get(str(program_id))


def program_id_from_filename(filename: str) -> str:
    match = re.match(r"^(\d+)", Path(filename).name)
    return match.group(1) if match else ""


def vintage_from_name(value: str) -> str:
    """Return a ``YYYY-MM`` vintage found in a filename or legacy dataset key."""

    match = re.search(r"(20\d{2})[-_](\d{2})(?:\D|$)", str(value))
    return f"{match.group(1)}-{match.group(2)}" if match else ""


def iter_parse_plan_files(path: Path = PARSE_PLANS_DIR) -> list[Path]:
    """Return parse-plan YAML files from either a file or a directory."""

    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted((*path.glob("*.yml"), *path.glob("*.yaml")))
    raise FileNotFoundError(f"Parse plan path does not exist: {path}")


def get_output_path(
    output_dir: Path,
    *,
    workbook: str,
    output_dataset: str,
) -> Path:
    """Return the canonical processed path for a source workbook release.

    Registered datasets use ``<dataset>/baseline_<YYYY-MM>.csv``.  The flat
    legacy location remains as a fallback for synthetic or unregistered inputs.
    """

    program_id = program_id_from_filename(workbook)
    dataset = dataset_for_program_id(program_id)
    # Curated parse-plan output keys include the release vintage. Synthetic or
    # ad-hoc output keys without a vintage retain the legacy flat-file path.
    vintage = vintage_from_name(output_dataset)
    if dataset is not None and vintage:
        return output_dir / dataset.key / f"baseline_{vintage}.csv"
    return output_dir / f"{output_dataset}.csv"
