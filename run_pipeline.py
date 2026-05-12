"""run_pipeline.py — canonical entrypoint for the CBO Baseline Detail pipeline.

Usage
-----
Run the full end-to-end pipeline:
    python run_pipeline.py

Run a single step:
    python run_pipeline.py --step download
    python run_pipeline.py --step inspect
    python run_pipeline.py --step transform
    python run_pipeline.py --step schema
    python run_pipeline.py --step verify

Each step logs its start time, completion time, and pass/fail status.
The runner stops on the first step failure.
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

# ---------------------------------------------------------------------------
# Step registry
# ---------------------------------------------------------------------------

STEP_NAMES = ("download", "inspect", "transform", "schema", "verify")


def _import_steps() -> dict[str, Callable[[], int]]:
    """Lazily import step functions to keep startup fast."""
    from src.download import run_download
    from src.workbook_inspector import run_inspection
    from src.transform import run_transform
    from src.generate_schemas import generate_schemas
    from src.verify import run_verification

    def _transform_all() -> int:
        return run_transform(slice_name="all")

    return {
        "download": run_download,
        "inspect": run_inspection,
        "transform": _transform_all,
        "schema": generate_schemas,
        "verify": run_verification,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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
        end_ts = _now_iso()
        print(f"[{end_ts}] STEP {name!r}: FAILED after {elapsed:.1f}s — {exc}")
        return False
    elapsed = time.monotonic() - start_wall
    end_ts = _now_iso()
    if exit_code == 0:
        print(f"[{end_ts}] STEP {name!r}: PASSED in {elapsed:.1f}s")
        return True
    print(f"[{end_ts}] STEP {name!r}: FAILED (exit code {exit_code}) in {elapsed:.1f}s")
    return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "CBO Baseline Detail pipeline runner. "
            "Runs all steps in order by default, or a single step with --step."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(
            [
                "Steps (run in this order):",
                "  download  — discover and download CBO workbooks to data/raw/",
                "  inspect   — profile workbooks and write docs/inspection_report.md",
                "  transform — parse all workbook sheets into CSV files in data/processed/",
                "  schema    — generate Markdown schema docs in docs/schemas/",
                "  verify    — reconcile processed CSVs against source values; write docs/verification_report.md",
            ]
        ),
    )
    parser.add_argument(
        "--step",
        choices=STEP_NAMES,
        default=None,
        help="Run a single named step instead of the full pipeline.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    steps = _import_steps()

    names_to_run = [args.step] if args.step else list(STEP_NAMES)
    overall_start = _now_iso()
    print(f"[{overall_start}] Pipeline starting — steps: {', '.join(names_to_run)}")

    for name in names_to_run:
        ok = _run_step(name, steps[name])
        if not ok:
            print(f"Pipeline stopped after step {name!r} failed.")
            return 1

    overall_end = _now_iso()
    print(f"[{overall_end}] Pipeline complete — all steps passed.")
    return 0


if __name__ == "__main__":
    # Ensure the repo root is on sys.path so `src.*` imports resolve correctly
    # whether the script is run as `python run_pipeline.py` or `python -m run_pipeline`.
    _repo_root = Path(__file__).resolve().parent
    if str(_repo_root) not in sys.path:
        sys.path.insert(0, str(_repo_root))
    raise SystemExit(main())
