"""Build the complete CBO Baseline Detail repository.

Usage:
    python scripts/run_pipeline.py
    python scripts/run_pipeline.py --step transform

The runner logs each step and stops after the first failure.
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


STEP_NAMES = ("download", "inspect", "transform", "schema", "verify")


def _import_steps() -> dict[str, Callable[[], int]]:
    """Lazily import step functions to keep startup fast."""

    from etl.download import run_download
    from etl.inspect import run_inspection
    from etl.schema import generate_schemas
    from etl.transform import run_transform
    from etl.validate import run_verification

    def _transform_all() -> int:
        return run_transform(slice_name="all")

    return {
        "download": run_download,
        "inspect": run_inspection,
        "transform": _transform_all,
        "schema": generate_schemas,
        "verify": run_verification,
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_step(name: str, fn: Callable[[], int]) -> bool:
    """Run one pipeline step, print timing, and return True on success."""

    start_ts = _now_iso()
    start_wall = time.monotonic()
    print(f"[{start_ts}] STEP {name!r}: starting")
    try:
        exit_code = fn()
    except Exception as exc:  # noqa: BLE001
        elapsed = time.monotonic() - start_wall
        print(f"[{_now_iso()}] STEP {name!r}: FAILED after {elapsed:.1f}s — {exc}")
        return False
    elapsed = time.monotonic() - start_wall
    if exit_code == 0:
        print(f"[{_now_iso()}] STEP {name!r}: PASSED in {elapsed:.1f}s")
        return True
    print(f"[{_now_iso()}] STEP {name!r}: FAILED (exit code {exit_code}) in {elapsed:.1f}s")
    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "CBO Baseline Detail pipeline runner. Runs every step in order by default, "
            "or a single step with --step."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(
            [
                "Steps (run in this order):",
                "  download  — discover and download CBO workbooks to data/raw/",
                "  inspect   — profile workbooks and write docs/inspection_report.md",
                "  transform — write versioned CSVs under data/processed/<dataset>/",
                "  schema    — write stable schemas, release metadata, and catalog.json",
                "  verify    — reconcile processed rows and write docs/verification_report.md",
            ]
        ),
    )
    parser.add_argument(
        "--step",
        choices=STEP_NAMES,
        default=None,
        help="Run a single named step instead of the complete pipeline.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    steps = _import_steps()
    names_to_run = [args.step] if args.step else list(STEP_NAMES)
    print(f"[{_now_iso()}] Pipeline starting — steps: {', '.join(names_to_run)}")

    for name in names_to_run:
        if not _run_step(name, steps[name]):
            print(f"Pipeline stopped after step {name!r} failed.")
            return 1

    print(f"[{_now_iso()}] Pipeline complete — all steps passed.")
    return 0


if __name__ == "__main__":
    # Direct execution places scripts/ rather than the repository root on
    # sys.path. Add the root so the importable etl package resolves.
    repo_root = Path(__file__).resolve().parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    raise SystemExit(main())
