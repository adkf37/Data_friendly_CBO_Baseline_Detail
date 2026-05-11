from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

if sys.path:
    script_dir = Path(__file__).resolve().parent
    if Path(sys.path[0]).resolve() == script_dir:
        sys.path[0] = str(script_dir.parent)

from dataclasses import dataclass

import yaml
from openpyxl import load_workbook

from src import transform

RELATIVE_TOLERANCE = 0.0001  # 0.01%


@dataclass(frozen=True)
class VerificationPlan:
    workbook: str
    sheet: str
    include: bool
    output_dataset: str
    verification_target: str
    header_end_row: int
    first_data_row: int | None
    year_columns: list[int]
    unit: str
    verification_include_totals: bool
    verification_exempt: bool
    verification_exempt_reason: str


@dataclass(frozen=True)
class YearComparison:
    fiscal_year: int
    source_total: float
    processed_total: float
    absolute_diff: float
    relative_diff: float | None
    passed: bool


@dataclass(frozen=True)
class VerificationResult:
    plan: VerificationPlan
    status: str
    absolute_tolerance: float
    relative_tolerance: float
    comparisons: list[YearComparison]
    notes: list[str]


def _read_plan(parse_plan_path: Path) -> list[VerificationPlan]:
    payload = yaml.safe_load(parse_plan_path.read_text(encoding="utf-8")) or {}
    plans: list[VerificationPlan] = []
    for workbook_entry in payload.get("workbooks", []):
        workbook_name = workbook_entry.get("workbook", "")
        for sheet_entry in workbook_entry.get("sheets", []):
            plans.append(
                VerificationPlan(
                    workbook=workbook_name,
                    sheet=sheet_entry.get("sheet", ""),
                    include=bool(sheet_entry.get("include")),
                    output_dataset=sheet_entry.get("output_dataset", ""),
                    verification_target=sheet_entry.get("verification_target", ""),
                    header_end_row=transform._header_end_row(str(sheet_entry.get("header_rows", "1-1"))),
                    first_data_row=sheet_entry.get("first_data_row"),
                    year_columns=[int(column) for column in sheet_entry.get("year_columns", [])],
                    unit=str(sheet_entry.get("unit", "")).strip(),
                    verification_include_totals=bool(sheet_entry.get("verification_include_totals", False)),
                    verification_exempt=bool(sheet_entry.get("verification_exempt", False)),
                    verification_exempt_reason=str(sheet_entry.get("verification_exempt_reason", "")).strip(),
                )
            )
    return plans


def _absolute_tolerance_for_unit(unit: str) -> float:
    lowered = unit.lower()
    if "billion" in lowered:
        return 0.001
    if "million" in lowered:
        return 0.01
    if "thousand" in lowered:
        return 1.0
    if "percent" in lowered or "share" in lowered or "rate" in lowered:
        return 0.001
    return 0.01


def _target_name(plan: VerificationPlan) -> str:
    if plan.verification_target:
        return plan.verification_target
    return f"{plan.output_dataset}:{plan.sheet}"


def _aggregate_source_totals(plan: VerificationPlan, input_dir: Path) -> tuple[dict[int, float], list[str]]:
    notes: list[str] = []
    workbook_path = input_dir / plan.workbook
    if not workbook_path.exists():
        return {}, [f"workbook missing: {plan.workbook}"]
    if not plan.year_columns:
        return {}, ["parse plan has no year_columns"]

    workbook = load_workbook(workbook_path, read_only=True, data_only=True)
    try:
        if plan.sheet not in workbook.sheetnames:
            return {}, [f"sheet missing: {plan.sheet}"]
        worksheet = workbook[plan.sheet]
        sheet_plan = transform.SheetPlan(
            workbook=plan.workbook,
            sheet=plan.sheet,
            include=plan.include,
            output_dataset=plan.output_dataset,
            header_end_row=plan.header_end_row,
            first_data_row=plan.first_data_row,
            year_columns=plan.year_columns,
            unit=plan.unit,
        )
        years = transform._extract_years(worksheet, sheet_plan)
        if not years:
            return {}, ["no fiscal years inferred from source"]

        first_data_row = plan.first_data_row or transform._infer_first_data_row(worksheet, sheet_plan)
        if first_data_row is None:
            return {}, ["could not infer first data row"]

        totals_by_year: dict[int, float] = {}
        rows_seen = 0
        for row in range(first_data_row, worksheet.max_row + 1):
            category = transform._to_text(worksheet.cell(row=row, column=1).value)
            if not category or transform._looks_like_note(category):
                continue
            if not plan.verification_include_totals and transform._is_total(category):
                continue
            for column in plan.year_columns:
                fiscal_year = years.get(column)
                if fiscal_year is None:
                    continue
                value = transform._parse_number(worksheet.cell(row=row, column=column).value)
                if value is None:
                    continue
                totals_by_year[fiscal_year] = totals_by_year.get(fiscal_year, 0.0) + value
                rows_seen += 1
        if rows_seen == 0:
            notes.append("no numeric source values found in scoped rows")
        return totals_by_year, notes
    finally:
        workbook.close()


def _aggregate_processed_totals(plan: VerificationPlan, processed_dir: Path) -> tuple[dict[int, float], list[str]]:
    notes: list[str] = []
    csv_path = processed_dir / f"{plan.output_dataset}.csv"
    if not csv_path.exists():
        return {}, [f"processed CSV missing: {csv_path.name}"]

    totals_by_year: dict[int, float] = {}
    rows_seen = 0
    with csv_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("source_file") != plan.workbook or row.get("source_sheet") != plan.sheet:
                continue
            if not plan.verification_include_totals and row.get("is_total", "").strip().lower() == "true":
                continue
            year_text = (row.get("fiscal_year") or "").strip()
            value_text = (row.get("value") or "").strip()
            if not year_text or not value_text:
                continue
            try:
                fiscal_year = int(float(year_text))
                value = float(value_text)
            except ValueError:
                notes.append(f"invalid processed row values: fiscal_year={year_text!r}, value={value_text!r}")
                continue
            totals_by_year[fiscal_year] = totals_by_year.get(fiscal_year, 0.0) + value
            rows_seen += 1
    if rows_seen == 0:
        notes.append("no processed rows matched source_file/source_sheet scope")
    return totals_by_year, notes


def _compare(plan: VerificationPlan, source_totals: dict[int, float], processed_totals: dict[int, float], notes: list[str]) -> VerificationResult:
    absolute_tolerance = _absolute_tolerance_for_unit(plan.unit)
    comparisons: list[YearComparison] = []
    all_years = sorted(set(source_totals) | set(processed_totals))
    if not all_years:
        notes = [*notes, "no comparable fiscal years found"]

    for fiscal_year in all_years:
        source_total = source_totals.get(fiscal_year, 0.0)
        processed_total = processed_totals.get(fiscal_year, 0.0)
        absolute_diff = abs(source_total - processed_total)
        if source_total == 0:
            relative_diff = None
            relative_ok = absolute_diff <= absolute_tolerance
        else:
            relative_diff = absolute_diff / abs(source_total)
            relative_ok = relative_diff <= RELATIVE_TOLERANCE
        passed = absolute_diff <= absolute_tolerance or relative_ok
        comparisons.append(
            YearComparison(
                fiscal_year=fiscal_year,
                source_total=source_total,
                processed_total=processed_total,
                absolute_diff=absolute_diff,
                relative_diff=relative_diff,
                passed=passed,
            )
        )

    failed = not comparisons or any(not comparison.passed for comparison in comparisons) or any(
        note.startswith(("workbook missing", "sheet missing", "processed CSV missing")) for note in notes
    )
    status = "PASS"
    if failed and plan.verification_exempt:
        status = "EXEMPT"
    elif failed:
        status = "FAIL"

    if plan.verification_exempt and plan.verification_exempt_reason:
        notes = [*notes, f"exempt reason: {plan.verification_exempt_reason}"]

    return VerificationResult(
        plan=plan,
        status=status,
        absolute_tolerance=absolute_tolerance,
        relative_tolerance=RELATIVE_TOLERANCE,
        comparisons=comparisons,
        notes=notes,
    )


def _render_report(results: list[VerificationResult]) -> str:
    non_exempt_failures = sum(1 for result in results if result.status == "FAIL")
    passes = sum(1 for result in results if result.status == "PASS")
    exempt = sum(1 for result in results if result.status == "EXEMPT")

    lines: list[str] = [
        "# Verification Report",
        "",
        "Generated by `python src/verify.py`.",
        "",
        "## Summary",
        "",
        f"- Verification targets: {len(results)}",
        f"- Pass: {passes}",
        f"- Exempt failures: {exempt}",
        f"- Non-exempt failures: {non_exempt_failures}",
        "",
        "## Target Status",
        "",
        "| Target | Dataset | Source | Status | Notes |",
        "|---|---|---|---|---|",
    ]

    for result in results:
        target = _target_name(result.plan)
        source = f"{result.plan.workbook} :: {result.plan.sheet}"
        notes = "; ".join(result.notes) if result.notes else ""
        lines.append(
            f"| `{target}` | `{result.plan.output_dataset}` | `{source}` | **{result.status}** | {notes or '—'} |"
        )

    lines.extend(["", "## Fiscal-Year Variance Details", ""])

    for result in results:
        target = _target_name(result.plan)
        lines.append(f"### `{target}`")
        lines.append("")
        lines.append(f"- Dataset: `{result.plan.output_dataset}`")
        lines.append(f"- Source: `{result.plan.workbook}` / `{result.plan.sheet}`")
        lines.append(f"- Status: **{result.status}**")
        lines.append(
            f"- Tolerances: absolute ≤ `{result.absolute_tolerance}` ({result.plan.unit or 'unit unspecified'}), "
            f"relative ≤ `{result.relative_tolerance * 100:.2f}%`"
        )
        lines.append(
            f"- Compare totals rows: {'included' if result.plan.verification_include_totals else 'excluded (default)'}"
        )
        if result.notes:
            lines.append(f"- Notes: {'; '.join(result.notes)}")
        lines.append("")
        lines.append("| Fiscal Year | Source Total | Processed Total | Absolute Diff | Relative Diff | Result |")
        lines.append("|---|---:|---:|---:|---:|---|")
        if result.comparisons:
            for comparison in result.comparisons:
                relative = "n/a" if comparison.relative_diff is None else f"{comparison.relative_diff * 100:.6f}%"
                lines.append(
                    f"| {comparison.fiscal_year} | {comparison.source_total:.6f} | "
                    f"{comparison.processed_total:.6f} | {comparison.absolute_diff:.6f} | {relative} | "
                    f"{'PASS' if comparison.passed else 'FAIL'} |"
                )
        else:
            lines.append("| — | 0.000000 | 0.000000 | 0.000000 | n/a | FAIL |")
        lines.append("")

    return "\n".join(lines) + "\n"


def run_verification(
    parse_plan_path: Path = Path("config/workbook_parse_plan.yaml"),
    input_dir: Path = Path("data/raw"),
    processed_dir: Path = Path("data/processed"),
    report_path: Path = Path("docs/verification_report.md"),
) -> int:
    plans = [plan for plan in _read_plan(parse_plan_path) if plan.include]
    results: list[VerificationResult] = []

    for plan in plans:
        source_totals, source_notes = _aggregate_source_totals(plan, input_dir)
        processed_totals, processed_notes = _aggregate_processed_totals(plan, processed_dir)
        result = _compare(plan, source_totals, processed_totals, [*source_notes, *processed_notes])
        results.append(result)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_render_report(results), encoding="utf-8")

    non_exempt_failures = sum(1 for result in results if result.status == "FAIL")
    print(
        "Verification complete. "
        f"targets={len(results)}, pass={sum(1 for result in results if result.status == 'PASS')}, "
        f"exempt={sum(1 for result in results if result.status == 'EXEMPT')}, "
        f"non_exempt_failures={non_exempt_failures}, report={report_path}"
    )
    return 1 if non_exempt_failures else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify processed CBO CSV outputs against source workbook values.")
    parser.add_argument("--parse-plan", type=Path, default=Path("config/workbook_parse_plan.yaml"))
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--report", type=Path, default=Path("docs/verification_report.md"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return run_verification(
        parse_plan_path=args.parse_plan,
        input_dir=args.input_dir,
        processed_dir=args.processed_dir,
        report_path=args.report,
    )


if __name__ == "__main__":
    raise SystemExit(main())
