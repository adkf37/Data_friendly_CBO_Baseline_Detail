import csv
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from src import verify


def _write_workbook(path: Path) -> None:
    workbook = Workbook()
    passing = workbook.active
    passing.title = "Passing"
    passing["A1"] = "Category"
    passing["B1"] = "2025"
    passing["C1"] = "2026"
    passing["A2"] = "Total Outlays"
    passing["B2"] = 100
    passing["C2"] = 110
    passing["A3"] = "Program Detail"
    passing["B3"] = 30
    passing["C3"] = 31

    failing = workbook.create_sheet("Failing")
    failing["A1"] = "Category"
    failing["B1"] = "2025"
    failing["C1"] = "2026"
    failing["A2"] = "Total Outlays"
    failing["B2"] = 200
    failing["C2"] = 210
    failing["A3"] = "Program Detail"
    failing["B3"] = 60
    failing["C3"] = 61
    workbook.save(path)


def _write_processed_csv(path: Path, workbook: str, sheet: str, values: list[tuple[str, int, float, bool]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "program",
                "category",
                "fiscal_year",
                "value",
                "unit",
                "source_file",
                "source_sheet",
                "is_total",
            ],
        )
        writer.writeheader()
        for category, fiscal_year, value, is_total in values:
            writer.writerow(
                {
                    "program": "Synthetic",
                    "category": category,
                    "fiscal_year": fiscal_year,
                    "value": value,
                    "unit": "Millions of dollars",
                    "source_file": workbook,
                    "source_sheet": sheet,
                    "is_total": str(is_total).lower(),
                }
            )


class VerifyTests(unittest.TestCase):
    def test_verification_returns_nonzero_on_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            raw_dir = root / "raw"
            processed_dir = root / "processed"
            raw_dir.mkdir(parents=True)

            workbook_name = "51293-2024-06-childnutrition.xlsx"
            _write_workbook(raw_dir / workbook_name)

            parse_plan = root / "workbook_parse_plan.yaml"
            parse_plan.write_text(
                """
workbooks:
  - workbook: 51293-2024-06-childnutrition.xlsx
    sheets:
      - sheet: Passing
        include: true
        output_dataset: pass_dataset
        verification_target: pass-target
        header_rows: 1-1
        first_data_row: 2
        year_columns: [2, 3]
        unit: Millions of dollars
      - sheet: Failing
        include: true
        output_dataset: fail_dataset
        verification_target: fail-target
        header_rows: 1-1
        first_data_row: 2
        year_columns: [2, 3]
        unit: Millions of dollars
                """.strip()
                + "\n",
                encoding="utf-8",
            )

            _write_processed_csv(
                processed_dir / "pass_dataset.csv",
                workbook=workbook_name,
                sheet="Passing",
                values=[
                    ("Total Outlays", 2025, 999, True),
                    ("Total Outlays", 2026, 999, True),
                    ("Program Detail", 2025, 30, False),
                    ("Program Detail", 2026, 31, False),
                ],
            )
            _write_processed_csv(
                processed_dir / "fail_dataset.csv",
                workbook=workbook_name,
                sheet="Failing",
                values=[
                    ("Program Detail", 2025, 60, False),
                    ("Program Detail", 2026, 999, False),
                ],
            )

            report_path = root / "verification_report.md"
            rc = verify.run_verification(
                parse_plan_path=parse_plan,
                input_dir=raw_dir,
                processed_dir=processed_dir,
                report_path=report_path,
            )

            self.assertEqual(1, rc)
            report = report_path.read_text(encoding="utf-8")
            self.assertIn("Verification targets: 2", report)
            self.assertIn("Non-exempt failures: 1", report)
            self.assertIn("`pass-target`", report)
            self.assertIn("Status: **PASS**", report)
            self.assertIn("`fail-target`", report)
            self.assertIn("Status: **FAIL**", report)
            self.assertIn("| 2026 | 61.000000 | 999.000000", report)

    def test_verification_include_totals_affects_pass_fail_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            raw_dir = root / "raw"
            processed_dir = root / "processed"
            raw_dir.mkdir(parents=True)

            workbook_name = "51293-2024-06-childnutrition.xlsx"
            _write_workbook(raw_dir / workbook_name)

            _write_processed_csv(
                processed_dir / "pass_dataset.csv",
                workbook=workbook_name,
                sheet="Passing",
                values=[
                    ("Total Outlays", 2025, 999, True),
                    ("Total Outlays", 2026, 999, True),
                    ("Program Detail", 2025, 30, False),
                    ("Program Detail", 2026, 31, False),
                ],
            )

            parse_plan_default = root / "parse_default.yaml"
            parse_plan_default.write_text(
                """
workbooks:
  - workbook: 51293-2024-06-childnutrition.xlsx
    sheets:
      - sheet: Passing
        include: true
        output_dataset: pass_dataset
        verification_target: pass-default
        header_rows: 1-1
        first_data_row: 2
        year_columns: [2, 3]
        unit: Millions of dollars
                """.strip()
                + "\n",
                encoding="utf-8",
            )
            parse_plan_include_totals = root / "parse_include_totals.yaml"
            parse_plan_include_totals.write_text(
                """
workbooks:
  - workbook: 51293-2024-06-childnutrition.xlsx
    sheets:
      - sheet: Passing
        include: true
        output_dataset: pass_dataset
        verification_target: pass-include-totals
        header_rows: 1-1
        first_data_row: 2
        year_columns: [2, 3]
        unit: Millions of dollars
        verification_include_totals: true
                """.strip()
                + "\n",
                encoding="utf-8",
            )

            report_default = root / "default_report.md"
            rc_default = verify.run_verification(
                parse_plan_path=parse_plan_default,
                input_dir=raw_dir,
                processed_dir=processed_dir,
                report_path=report_default,
            )
            self.assertEqual(0, rc_default)
            self.assertIn("Status: **PASS**", report_default.read_text(encoding="utf-8"))

            report_include = root / "include_report.md"
            rc_include = verify.run_verification(
                parse_plan_path=parse_plan_include_totals,
                input_dir=raw_dir,
                processed_dir=processed_dir,
                report_path=report_include,
            )
            self.assertEqual(1, rc_include)
            self.assertIn("Status: **FAIL**", report_include.read_text(encoding="utf-8"))

    def test_verification_infers_year_columns_when_missing_from_parse_plan(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            raw_dir = root / "raw"
            processed_dir = root / "processed"
            raw_dir.mkdir(parents=True)

            workbook_name = "51293-2024-06-childnutrition.xlsx"
            _write_workbook(raw_dir / workbook_name)
            _write_processed_csv(
                processed_dir / "pass_dataset.csv",
                workbook=workbook_name,
                sheet="Passing",
                values=[
                    ("Program Detail", 2025, 30, False),
                    ("Program Detail", 2026, 31, False),
                ],
            )

            parse_plan_path = root / "parse_missing_year_columns.yaml"
            parse_plan_path.write_text(
                """
workbooks:
  - workbook: 51293-2024-06-childnutrition.xlsx
    sheets:
      - sheet: Passing
        include: true
        output_dataset: pass_dataset
        verification_target: pass-missing-year-columns
        header_rows: 1-1
        first_data_row: 2
        unit: Millions of dollars
                """.strip()
                + "\n",
                encoding="utf-8",
            )

            report_path = root / "verification_report.md"
            rc = verify.run_verification(
                parse_plan_path=parse_plan_path,
                input_dir=raw_dir,
                processed_dir=processed_dir,
                report_path=report_path,
            )

            self.assertEqual(0, rc)
            report = report_path.read_text(encoding="utf-8")
            self.assertIn("`pass-missing-year-columns`", report)
            self.assertIn("Status: **PASS**", report)


if __name__ == "__main__":
    unittest.main()
