"""Rebuild ``catalog.json`` from existing schemas and release metadata."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from etl.config import CATALOG_PATH, PROCESSED_DIR  # noqa: E402
from etl.schema import build_catalog  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Build catalog.json from processed datasets.")
    parser.add_argument("--processed-dir", type=Path, default=PROCESSED_DIR)
    parser.add_argument("--catalog", type=Path, default=CATALOG_PATH)
    args = parser.parse_args()
    return build_catalog(processed_dir=args.processed_dir, catalog_path=args.catalog)


if __name__ == "__main__":
    raise SystemExit(main())
