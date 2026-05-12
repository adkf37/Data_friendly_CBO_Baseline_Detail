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
    def test_child_nutrition_dataset_routes_to_remaining_programs_slice(self):
        plan = transform.SheetPlan(
            workbook="51293-2024-06-childnutrition.xlsx",
            sheet="CNP",
            include=True,
            output_dataset="childnutrition_2024_06",
            header_end_row=1,
            first_data_row=2,
            year_columns=[2, 3],
            unit="Millions of dollars",
        )

        self.assertFalse(transform._in_slice(plan, "health"))
        self.assertTrue(transform._in_slice(plan, "remaining-programs"))

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

    def test_run_transform_prefers_header_years_over_in_data_years(self):
        """Header-declared years are preferred over stale in-data years.

        Rows with the same category but *different* values represent distinct
        sub-programs and must both appear in the output.  All source rows are
        preserved; the transform does not deduplicate rows with coincidentally
        identical values.
        """
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
            # Stale year value in the data area — must not become a fiscal year label.
            sheet["B2"] = 2096
            # Two distinct sub-program rows (different values → both kept).
            sheet["A3"] = "Paid"
            sheet["B3"] = 200
            sheet["C3"] = 210
            sheet["A4"] = "Free"
            sheet["B4"] = 50
            sheet["C4"] = 55
            # Row 5 has the same category and values as row 3; both rows are
            # written because each source row is preserved without deduplication.
            sheet["A5"] = "Paid"
            sheet["B5"] = 200
            sheet["C5"] = 210
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

            # 3 source rows × 2 fiscal years = 6 rows; rows 3 and 5 both appear
            # since every source row is preserved regardless of value equality.
            self.assertEqual(6, len(rows))
            fiscal_years = [row["fiscal_year"] for row in rows]
            self.assertEqual(["2024", "2025", "2024", "2025", "2024", "2025"], fiscal_years)
            values = [row["value"] for row in rows]
            self.assertEqual(["200.0", "210.0", "50.0", "55.0", "200.0", "210.0"], values)
            self.assertNotIn("2096", fiscal_years)

    def test_extract_years_scans_beyond_header_end_row(self):
        """Years in a row below the declared header_end_row are still found."""
        workbook = Workbook()
        ws = workbook.active
        ws.title = "Data"
        # Row 1 (header): category label only — no year values
        ws["A1"] = "Category"
        # Row 4: year values as integers (below header_rows: 1-1)
        ws["B4"] = 2020
        ws["C4"] = 2021
        # Row 5: data
        ws["A5"] = "Budget Authority"
        ws["B5"] = 100
        ws["C5"] = 110

        plan = transform.SheetPlan(
            workbook="test.xlsx",
            sheet="Data",
            include=True,
            output_dataset="test_dataset",
            header_end_row=1,  # declared header covers only row 1
            first_data_row=5,
            year_columns=[2, 3],
            unit="Millions of dollars",
        )

        years = transform._extract_years(ws, plan)
        self.assertEqual({2: 2020, 3: 2021}, years, "Years below declared header_end_row must be found")

    def test_extract_years_skips_datetime_cells(self):
        """Datetime objects (publication dates) in year columns must not be treated as fiscal years."""
        import datetime as dt

        workbook = Workbook()
        ws = workbook.active
        ws.title = "Data"
        # Row 1: a publication date datetime in column 2 — must not become a fiscal year label
        ws.cell(row=1, column=2).value = dt.datetime(2020, 5, 2)
        # Row 2: actual integer year value in column 2
        ws.cell(row=2, column=2).value = 2025
        ws.cell(row=3, column=1).value = "Program Detail"
        ws.cell(row=3, column=2).value = 500

        plan = transform.SheetPlan(
            workbook="test.xlsx",
            sheet="Data",
            include=True,
            output_dataset="test_dataset",
            header_end_row=1,
            first_data_row=3,
            year_columns=[2],
            unit="Millions",
        )

        years = transform._extract_years(ws, plan)
        # The datetime in row 1 must be skipped; row 2 (integer 2025) is not in
        # the declared header, but MAX_YEAR_SCAN_ROWS extends the search.
        self.assertEqual({2: 2025}, years, "datetime cell must be ignored; integer year row must be found")

    def test_find_sheet_exact_match(self):
        self.assertEqual("MySheet", transform._find_sheet(["MySheet", "Other"], "MySheet"))

    def test_find_sheet_trailing_space_match(self):
        """Sheet names with trailing spaces in the workbook are matched against the parse plan entry."""
        self.assertEqual("MySheet ", transform._find_sheet(["MySheet ", "Other"], "MySheet"))

    def test_find_sheet_returns_none_when_not_found(self):
        self.assertIsNone(transform._find_sheet(["Other", "Another"], "Missing"))

    def test_run_transform_handles_trailing_space_sheet_name(self):
        """Transform succeeds when the workbook sheet has a trailing space not in the parse plan."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_dir = root / "raw"
            output_dir = root / "processed"
            input_dir.mkdir(parents=True)

            workbook_name = "51297-2020-03-mortgages.xlsx"
            wb = Workbook()
            ws = wb.active
            ws.title = "Mortgage Programs "  # trailing space
            ws["A1"] = "Category"
            ws["B1"] = "2025"
            ws["A2"] = "Total Outlays"
            ws["B2"] = 500
            wb.save(input_dir / workbook_name)

            parse_plan = root / "workbook_parse_plan.yaml"
            parse_plan.write_text(
                """
workbooks:
  - workbook: 51297-2020-03-mortgages.xlsx
    sheets:
      - sheet: Mortgage Programs
        include: true
        output_dataset: mortgages_2020_03
        header_rows: 1-1
        first_data_row: 2
        year_columns: [2]
        unit: Millions of dollars
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
            csv_path = output_dir / "mortgages_2020_03.csv"
            self.assertTrue(csv_path.exists(), "CSV should be written even when sheet name has trailing space")


if __name__ == "__main__":
    unittest.main()
