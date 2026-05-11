import tempfile
import unittest
from csv import DictReader
from pathlib import Path

from openpyxl import Workbook

from src import transform


def _write_health_workbook(path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Health"
    sheet["A1"] = "Health Program"
    sheet["B1"] = "2025"
    sheet["C1"] = "2026"
    sheet["A2"] = "Total Benefits"
    sheet["B2"] = 100
    sheet["C2"] = 110
    sheet["A3"] = "Administrative Costs"
    sheet["B3"] = 20
    sheet["C3"] = 22
    workbook.save(path)


def _write_income_security_workbook(path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Income Security"
    sheet["A1"] = "Income Security Program"
    sheet["B1"] = "2025"
    sheet["C1"] = "2026"
    sheet["A2"] = "Total Benefits"
    sheet["B2"] = 100
    sheet["C2"] = 110
    sheet["A3"] = "Administrative Costs"
    sheet["B3"] = 20
    sheet["C3"] = 22
    workbook.save(path)


class TransformTests(unittest.TestCase):
    def test_run_transform_income_security_slice_excludes_health_datasets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir = root / "raw"
            output_dir = root / "processed"
            input_dir.mkdir(parents=True)

            health_workbook = "51293-2024-06-childnutrition.xlsx"
            income_workbook = "51312-2024-06-snap.xlsx"
            _write_health_workbook(input_dir / health_workbook)
            _write_income_security_workbook(input_dir / income_workbook)
            parse_plan = root / "workbook_parse_plan.yaml"
            parse_plan.write_text(
                """
workbooks:
  - workbook: 51293-2024-06-childnutrition.xlsx
    sheets:
      - sheet: Health
        include: true
        output_dataset: childnutrition_health_2024_06
        header_rows: 1-1
        first_data_row: 2
        year_columns: [2, 3]
        unit: Millions of dollars
  - workbook: 51312-2024-06-snap.xlsx
    sheets:
      - sheet: Income Security
        include: true
        output_dataset: snap_2024_06
        header_rows: 1-1
        first_data_row: 2
        year_columns: [2, 3]
        unit: Millions of dollars
                """.strip()
                + "\n",
                encoding="utf-8",
            )

            rc = transform.run_transform(
                parse_plan_path=parse_plan,
                input_dir=input_dir,
                output_dir=output_dir,
                slice_name="income-security",
            )

            self.assertEqual(0, rc)
            self.assertFalse((output_dir / "childnutrition_health_2024_06.csv").exists())
            csv_path = output_dir / "snap_2024_06.csv"
            self.assertTrue(csv_path.exists())
            with csv_path.open(encoding="utf-8", newline="") as handle:
                rows = list(DictReader(handle))
            self.assertEqual(4, len(rows))
            self.assertEqual({"Snap"}, {row["program"] for row in rows})
            self.assertEqual({"51312-2024-06-snap.xlsx"}, {row["source_file"] for row in rows})
            self.assertEqual({"Income Security"}, {row["source_sheet"] for row in rows})
            self.assertEqual({"Total Benefits", "Administrative Costs"}, {row["category"] for row in rows})
            self.assertEqual({"2025", "2026"}, {row["fiscal_year"] for row in rows})
            self.assertEqual("", (output_dir / "parse_errors.log").read_text(encoding="utf-8"))

    def test_run_transform_health_slice_writes_tidy_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir = root / "raw"
            output_dir = root / "processed"
            input_dir.mkdir(parents=True)

            workbook_name = "51293-2024-06-childnutrition.xlsx"
            _write_health_workbook(input_dir / workbook_name)
            parse_plan = root / "workbook_parse_plan.yaml"
            parse_plan.write_text(
                """
workbooks:
  - workbook: 51293-2024-06-childnutrition.xlsx
    sheets:
      - sheet: Health
        include: true
        output_dataset: childnutrition_health_2024_06
        header_rows: 1-1
        first_data_row: 2
        year_columns: [2, 3]
        unit: Millions of dollars
                """.strip()
                + "\n",
                encoding="utf-8",
            )

            rc = transform.run_transform(
                parse_plan_path=parse_plan,
                input_dir=input_dir,
                output_dir=output_dir,
                slice_name="health",
            )

            self.assertEqual(0, rc)
            csv_path = output_dir / "childnutrition_health_2024_06.csv"
            self.assertTrue(csv_path.exists())
            with csv_path.open(encoding="utf-8", newline="") as handle:
                rows = list(DictReader(handle))
            self.assertEqual(transform.OUTPUT_COLUMNS, list(rows[0].keys()))
            self.assertEqual(4, len(rows))
            self.assertEqual(
                {
                    "program": "Childnutrition",
                    "category": "Total Benefits",
                    "fiscal_year": "2025",
                    "value": "100.0",
                    "unit": "Millions of dollars",
                    "source_file": workbook_name,
                    "source_sheet": "Health",
                    "is_total": "true",
                },
                rows[0],
            )
            self.assertEqual("Administrative Costs", rows[-1]["category"])
            self.assertEqual("2026", rows[-1]["fiscal_year"])
            self.assertEqual("22.0", rows[-1]["value"])

            parse_errors = (output_dir / "parse_errors.log").read_text(encoding="utf-8")
            self.assertEqual("", parse_errors)

    def test_run_transform_logs_parse_errors(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parse_plan = root / "workbook_parse_plan.yaml"
            parse_plan.write_text(
                """
workbooks:
  - workbook: missing-health.xlsx
    sheets:
      - sheet: Missing
        include: true
        output_dataset: health_missing_2024
        header_rows: 1-1
        first_data_row: 2
        year_columns: [2]
        unit: Millions
                """.strip()
                + "\n",
                encoding="utf-8",
            )

            rc = transform.run_transform(
                parse_plan_path=parse_plan,
                input_dir=root / "raw",
                output_dir=root / "processed",
                slice_name="health",
            )

            self.assertEqual(1, rc)
            error_text = (root / "processed" / "parse_errors.log").read_text(encoding="utf-8")
            self.assertIn("missing-health.xlsx", error_text)
            self.assertIn("workbook not found", error_text)

    def test_run_transform_remaining_programs_slice_excludes_health_and_income_security(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir = root / "raw"
            output_dir = root / "processed"
            input_dir.mkdir(parents=True)

            health_workbook = "51293-2024-06-childnutrition.xlsx"
            income_workbook = "51312-2024-06-snap.xlsx"
            other_workbook = "51315-2024-06-defense.xlsx"

            _write_health_workbook(input_dir / health_workbook)
            _write_income_security_workbook(input_dir / income_workbook)

            # Write a simple "other/remaining programs" workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Defense"
            ws["A1"] = "Defense Program"
            ws["B1"] = "2025"
            ws["C1"] = "2026"
            ws["A2"] = "Total Outlays"
            ws["B2"] = 800
            ws["C2"] = 850
            wb.save(input_dir / other_workbook)

            parse_plan = root / "workbook_parse_plan.yaml"
            parse_plan.write_text(
                """
workbooks:
  - workbook: 51293-2024-06-childnutrition.xlsx
    sheets:
      - sheet: Health
        include: true
        output_dataset: childnutrition_health_2024_06
        header_rows: 1-1
        first_data_row: 2
        year_columns: [2, 3]
        unit: Millions of dollars
  - workbook: 51312-2024-06-snap.xlsx
    sheets:
      - sheet: Income Security
        include: true
        output_dataset: snap_2024_06
        header_rows: 1-1
        first_data_row: 2
        year_columns: [2, 3]
        unit: Millions of dollars
  - workbook: 51315-2024-06-defense.xlsx
    sheets:
      - sheet: Defense
        include: true
        output_dataset: defense_2024_06
        header_rows: 1-1
        first_data_row: 2
        year_columns: [2, 3]
        unit: Billions of dollars
                """.strip()
                + "\n",
                encoding="utf-8",
            )

            rc = transform.run_transform(
                parse_plan_path=parse_plan,
                input_dir=input_dir,
                output_dir=output_dir,
                slice_name="remaining-programs",
            )

            self.assertEqual(0, rc)
            self.assertFalse((output_dir / "childnutrition_health_2024_06.csv").exists())
            self.assertFalse((output_dir / "snap_2024_06.csv").exists())
            csv_path = output_dir / "defense_2024_06.csv"
            self.assertTrue(csv_path.exists())
            with csv_path.open(encoding="utf-8", newline="") as handle:
                rows = list(DictReader(handle))
            self.assertEqual(2, len(rows))
            self.assertEqual({"Defense"}, {row["program"] for row in rows})
            self.assertEqual({"2025", "2026"}, {row["fiscal_year"] for row in rows})
            self.assertEqual("", (output_dir / "parse_errors.log").read_text(encoding="utf-8"))

    def test_run_transform_rejects_unknown_slice(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            with self.assertRaisesRegex(ValueError, "Unsupported slice: unknown"):
                transform.run_transform(
                    parse_plan_path=root / "workbook_parse_plan.yaml",
                    input_dir=root / "raw",
                    output_dir=root / "processed",
                    slice_name="unknown",
                )

    def test_run_transform_excludes_pre_plausible_year_columns(self):
        """Year columns whose header year is before PLAUSIBLE_YEAR_MIN are silently dropped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir = root / "raw"
            output_dir = root / "processed"
            input_dir.mkdir(parents=True)

            workbook_name = "51302-2019-05-Medicare.xlsx"
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Table 1"
            # Column 2 = 2018 (prior-year actual — outside plausible range)
            # Column 3 = 2019, Column 4 = 2020 (plausible projection years)
            sheet["B1"] = 2018
            sheet["C1"] = 2019
            sheet["D1"] = 2020
            sheet["A2"] = "Total Outlays"
            sheet["B2"] = 700
            sheet["C2"] = 765
            sheet["D2"] = 814
            workbook.save(input_dir / workbook_name)

            parse_plan = root / "workbook_parse_plan.yaml"
            parse_plan.write_text(
                """
workbooks:
  - workbook: 51302-2019-05-Medicare.xlsx
    sheets:
      - sheet: Table 1
        include: true
        output_dataset: medicare_2019_05
        header_rows: 1-1
        first_data_row: 2
        year_columns: [2, 3, 4]
        unit: Medicare Totals (Billions of dollars)
                """.strip()
                + "\n",
                encoding="utf-8",
            )

            rc = transform.run_transform(
                parse_plan_path=parse_plan,
                input_dir=input_dir,
                output_dir=output_dir,
                slice_name="health",
            )

            self.assertEqual(0, rc)
            csv_path = output_dir / "medicare_2019_05.csv"
            self.assertTrue(csv_path.exists())
            with csv_path.open(encoding="utf-8", newline="") as handle:
                rows = list(DictReader(handle))

            fiscal_years = [row["fiscal_year"] for row in rows]
            self.assertNotIn("2018", fiscal_years, "Pre-2019 year column must be excluded")
            self.assertIn("2019", fiscal_years)
            self.assertIn("2020", fiscal_years)
            self.assertEqual(2, len(rows))

    def test_run_transform_prefers_header_years_and_deduplicates_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir = root / "raw"
            output_dir = root / "processed"
            input_dir.mkdir(parents=True)

            workbook_name = "51293-2024-06-childnutrition.xlsx"
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Health"
            sheet["A1"] = "Health Program"
            sheet["B1"] = "2024"
            sheet["C1"] = "2025"
            sheet["B2"] = 2096
            sheet["A3"] = "Paid"
            sheet["B3"] = 200
            sheet["C3"] = 210
            sheet["A4"] = "Paid"
            sheet["B4"] = 201
            sheet["C4"] = 211
            workbook.save(input_dir / workbook_name)

            parse_plan = root / "workbook_parse_plan.yaml"
            parse_plan.write_text(
                """
workbooks:
  - workbook: 51293-2024-06-childnutrition.xlsx
    sheets:
      - sheet: Health
        include: true
        output_dataset: childnutrition_health_2024_06
        header_rows: 1-4
        first_data_row: 3
        year_columns: [2, 3]
        unit: Millions
                """.strip()
                + "\n",
                encoding="utf-8",
            )

            rc = transform.run_transform(
                parse_plan_path=parse_plan,
                input_dir=input_dir,
                output_dir=output_dir,
                slice_name="health",
            )

            self.assertEqual(0, rc)
            csv_path = output_dir / "childnutrition_health_2024_06.csv"
            with csv_path.open(encoding="utf-8", newline="") as handle:
                rows = list(DictReader(handle))

            self.assertEqual(2, len(rows))
            self.assertEqual(["2024", "2025"], [row["fiscal_year"] for row in rows])
            self.assertEqual(["200.0", "210.0"], [row["value"] for row in rows])
            self.assertNotIn("2096", [row["fiscal_year"] for row in rows])


if __name__ == "__main__":
    unittest.main()
