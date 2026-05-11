from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

if sys.path:
    script_dir = Path(__file__).resolve().parent
    if Path(sys.path[0]).resolve() == script_dir:
        sys.path[0] = str(script_dir.parent)

from dataclasses import dataclass

import yaml
from openpyxl import load_workbook

YEAR_RE = re.compile(r"(19|20)\d{2}")
NUMBER_RE = re.compile(r"^\(?[$]?\s*[-+]?\d[\d,]*(?:\.\d+)?\)?$")
HEALTH_KEYWORDS = ("health", "medicare", "medicaid", "chip", "nutrition")
INCOME_SECURITY_KEYWORDS = (
    "child_support",
    "childsupport",
    "csec",
    "foster_care",
    "fostercare",
    "military_retirement",
    "militaryretirement",
    "snap",
    "social_security",
    "socialsecurity",
    "ssi",
    "student_loan",
    "studentloan",
    "tanf",
    "unemployment",
)
SLICE_KEYWORDS = {
    "health": HEALTH_KEYWORDS,
    "income-security": INCOME_SECURITY_KEYWORDS,
}
PLAUSIBLE_YEAR_MIN = 2019
PLAUSIBLE_YEAR_MAX = 2040

OUTPUT_COLUMNS = [
    "program",
    "category",
    "fiscal_year",
    "value",
    "unit",
    "source_file",
    "source_sheet",
    "is_total",
]


@dataclass(frozen=True)
class SheetPlan:
    workbook: str
    sheet: str
    include: bool
    output_dataset: str
    header_end_row: int
    first_data_row: int | None
    year_columns: list[int]
    unit: str


def _header_end_row(header_rows: str) -> int:
    if "-" in header_rows:
        _, end = header_rows.split("-", 1)
        return int(end)
    return int(header_rows)


def _to_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _parse_number(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = _to_text(value)
    if not text:
        return None
    if not NUMBER_RE.match(text):
        return None
    normalized = text.replace("$", "").replace(",", "").replace(" ", "")
    negative = normalized.startswith("(") and normalized.endswith(")")
    normalized = normalized.strip("()")
    parsed = float(normalized)
    return -parsed if negative else parsed


def _is_total(category: str) -> bool:
    lowered = category.lower()
    return "total" in lowered or "subtotal" in lowered


def _looks_like_note(category: str) -> bool:
    lowered = category.lower()
    return lowered.startswith("note") or lowered.startswith("source")


def _extract_years(worksheet, plan: SheetPlan) -> dict[int, int]:
    years: dict[int, int] = {}
    for column in plan.year_columns:
        for row in range(1, plan.header_end_row + 1):
            cell_text = _to_text(worksheet.cell(row=row, column=column).value)
            match = YEAR_RE.search(cell_text)
            if match:
                year = int(match.group(0))
                if PLAUSIBLE_YEAR_MIN <= year <= PLAUSIBLE_YEAR_MAX:
                    years[column] = year
                break
    return years


def _infer_first_data_row(worksheet, plan: SheetPlan) -> int | None:
    for row in range(plan.header_end_row + 1, worksheet.max_row + 1):
        category = _to_text(worksheet.cell(row=row, column=1).value)
        if not category:
            continue
        if _looks_like_note(category):
            continue
        parsed_values = [_parse_number(worksheet.cell(row=row, column=col).value) for col in plan.year_columns]
        has_value = any(value is not None for value in parsed_values)
        if has_value:
            return row
    return None


def _infer_program_name(filename: str) -> str:
    """Infer a display program name from CBO workbook filenames.

    Typical filenames follow `<id>-<year>-<month>-<program>.xlsx`, e.g.
    `51293-2024-06-childnutrition.xlsx`. If this shape is not present, the
    entire stem is used.
    """
    stem = Path(filename).stem.replace("_", "-")
    parts = stem.split("-")
    if len(parts) >= 4:
        name = "-".join(parts[3:])
    else:
        name = stem
    return " ".join(token for token in re.split(r"[-\s]+", name) if token).title()


def _read_plan(path: Path) -> list[SheetPlan]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    plans: list[SheetPlan] = []
    for workbook_entry in payload.get("workbooks", []):
        workbook_name = workbook_entry.get("workbook")
        for sheet_entry in workbook_entry.get("sheets", []):
            plans.append(
                SheetPlan(
                    workbook=workbook_name,
                    sheet=sheet_entry.get("sheet"),
                    include=bool(sheet_entry.get("include")),
                    output_dataset=sheet_entry.get("output_dataset", ""),
                    header_end_row=_header_end_row(str(sheet_entry.get("header_rows", "1-1"))),
                    first_data_row=sheet_entry.get("first_data_row"),
                    year_columns=[int(column) for column in sheet_entry.get("year_columns", [])],
                    unit=str(sheet_entry.get("unit", "")).strip(),
                )
            )
    return plans


def _in_slice(plan: SheetPlan, slice_name: str) -> bool:
    slice_name = slice_name.replace("_", "-").lower()
    if slice_name == "all":
        return True
    dataset = plan.output_dataset.lower()
    keywords = SLICE_KEYWORDS.get(slice_name, ())
    return any(keyword in dataset for keyword in keywords)


def _write_dataset(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _append_error(errors: list[str], workbook: str, sheet: str, reason: str) -> None:
    errors.append(f"{workbook}\t{sheet}\t{reason}")


def run_transform(
    parse_plan_path: Path = Path("config/workbook_parse_plan.yaml"),
    input_dir: Path = Path("data/raw"),
    output_dir: Path = Path("data/processed"),
    slice_name: str = "health",
) -> int:
    plans = [plan for plan in _read_plan(parse_plan_path) if plan.include and _in_slice(plan, slice_name)]
    records_by_dataset: dict[str, list[dict]] = defaultdict(list)
    seen_keys_by_dataset: dict[str, set[tuple[str, str, int, str, str]]] = defaultdict(set)
    errors: list[str] = []

    for plan in plans:
        workbook_path = input_dir / plan.workbook
        if not workbook_path.exists():
            _append_error(errors, plan.workbook, plan.sheet, "workbook not found")
            continue
        if not plan.year_columns:
            _append_error(errors, plan.workbook, plan.sheet, "year_columns missing")
            continue

        workbook = load_workbook(workbook_path, read_only=True, data_only=True)
        try:
            if plan.sheet not in workbook.sheetnames:
                _append_error(errors, plan.workbook, plan.sheet, "sheet not found")
                continue
            worksheet = workbook[plan.sheet]
            years = _extract_years(worksheet, plan)
            if not years:
                _append_error(errors, plan.workbook, plan.sheet, "no fiscal years inferred")
                continue
            first_data_row = plan.first_data_row or _infer_first_data_row(worksheet, plan)
            if first_data_row is None:
                _append_error(errors, plan.workbook, plan.sheet, "could not infer first data row")
                continue

            rows_written = 0
            program_name = _infer_program_name(plan.workbook)
            for row in range(first_data_row, worksheet.max_row + 1):
                category = _to_text(worksheet.cell(row=row, column=1).value)
                if not category:
                    continue
                if _looks_like_note(category):
                    continue
                for column in plan.year_columns:
                    year = years.get(column)
                    if year is None:
                        continue
                    value = _parse_number(worksheet.cell(row=row, column=column).value)
                    if value is None:
                        continue
                    key = (
                        program_name,
                        category,
                        year,
                        plan.unit,
                        plan.sheet,
                    )
                    if key in seen_keys_by_dataset[plan.output_dataset]:
                        continue
                    seen_keys_by_dataset[plan.output_dataset].add(key)
                    records_by_dataset[plan.output_dataset].append(
                        {
                            "program": program_name,
                            "category": category,
                            "fiscal_year": year,
                            "value": value,
                            "unit": plan.unit,
                            "source_file": plan.workbook,
                            "source_sheet": plan.sheet,
                            "is_total": str(_is_total(category)).lower(),
                        }
                    )
                    rows_written += 1
            if rows_written == 0:
                _append_error(errors, plan.workbook, plan.sheet, "no data rows parsed")
        finally:
            workbook.close()

    output_dir.mkdir(parents=True, exist_ok=True)
    for dataset, rows in records_by_dataset.items():
        _write_dataset(output_dir / f"{dataset}.csv", rows)

    error_path = output_dir / "parse_errors.log"
    error_body = "\n".join(errors)
    if errors:
        error_body += "\n"
    error_path.write_text(error_body, encoding="utf-8")
    print(
        f"Transform complete. slice={slice_name}, datasets={len(records_by_dataset)}, "
        f"rows={sum(len(rows) for rows in records_by_dataset.values())}, errors={len(errors)}"
    )
    return 1 if errors else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transform CBO baseline workbooks into tidy CSV datasets.")
    parser.add_argument("--parse-plan", type=Path, default=Path("config/workbook_parse_plan.yaml"))
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--slice", dest="slice_name", choices=["health", "income-security", "all"], default="health")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return run_transform(
        parse_plan_path=args.parse_plan,
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        slice_name=args.slice_name,
    )


if __name__ == "__main__":
    raise SystemExit(main())
