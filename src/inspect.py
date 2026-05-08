from __future__ import annotations

from pathlib import Path
import sys

if sys.path:
    script_dir = Path(__file__).resolve().parent
    if Path(sys.path[0]).resolve() == script_dir:
        sys.path[0] = str(script_dir.parent)

from src.workbook_inspector import (
    inspect_workbook,
    main,
    parse_args,
    profile_sheet,
    render_report,
    run_inspection,
)

__all__ = [
    "inspect_workbook",
    "main",
    "parse_args",
    "profile_sheet",
    "render_report",
    "run_inspection",
]


if __name__ == "__main__":
    raise SystemExit(main())
