import tempfile
import unittest
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


class TransformTests(unittest.TestCase):
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
            rows = csv_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(",".join(transform.OUTPUT_COLUMNS), rows[0])
            expected_program = transform._infer_program_name(workbook_name)
            self.assertIn(f"{expected_program},Total Benefits,2025,100.0,Millions of dollars,", rows[1])
            self.assertIn(",true", rows[1])
            self.assertIn("Administrative Costs,2026,22.0", rows[-1])

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


if __name__ == "__main__":
    unittest.main()
