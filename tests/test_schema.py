import json
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont

from etl import schema


def _write_sample_csv(
    path: Path,
    *,
    program: str = "SNAP",
    program_id: str = "51312",
    source_file: str = "51312-2024-06-snap.xlsx",
    source_sheet: str = "SNAP_06-2024",
    year: int = 2024,
    has_totals: bool = True,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        f"{program},Estimated Budget Authority,{year},103764.0,Millions of dollars,"
        f"{source_file},{source_sheet},false,{program_id},Estimated Budget Authority,"
        f"fiscal_year,{year},{year},{year},10,4\n"
    ]
    if has_totals:
        rows.append(
            f"{program},Total Outlays,{year},104000.0,Millions of dollars,"
            f"{source_file},{source_sheet},true,{program_id},Total Outlays,"
            f"fiscal_year,{year},{year},{year},11,4\n"
        )
    path.write_text(
        "program,category,fiscal_year,value,unit,source_file,source_sheet,is_total,"
        "program_id,category_path,period_type,period_start_year,period_end_year,"
        "period_label,source_row,source_column\n"
        + "".join(rows),
        encoding="utf-8",
    )


def _write_usda_sample_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "program,category,fiscal_year,value,unit,source_file,source_sheet,is_total,"
        "program_id,category_path,table_title,section,subsection,period_type,"
        "period_start_year,period_end_year,period_label,source_row,source_column\n"
        "USDA Farm Programs,Production,2026,100.0,Millions,51317-2026-02-usda.xlsx,"
        "USDA Baseline_02-2026,false,51317,CORN SUPPLY AND USE / Supply / Production,"
        "CORN SUPPLY AND USE,Supply,,fiscal_year,2026,2026,2026,10,4\n",
        encoding="utf-8",
    )


def _generate(root: Path, *, raw_dir: Path | None = None) -> int:
    return schema.generate_schemas(
        processed_dir=root / "processed",
        schemas_dir=root / "schemas",
        raw_dir=raw_dir if raw_dir is not None else root / "missing-raw",
        catalog_path=root / "catalog.json",
    )


class GenerateSchemasTests(unittest.TestCase):
    def test_one_stable_schema_covers_multiple_releases(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            dataset_dir = root / "processed" / "snap"
            _write_sample_csv(dataset_dir / "baseline_2024-06.csv")
            _write_sample_csv(
                dataset_dir / "baseline_2026-02.csv",
                source_file="51312-2026-02-snap.xlsx",
                source_sheet="SNAP_02-2026",
                year=2026,
            )

            self.assertEqual(0, _generate(root))
            self.assertTrue((dataset_dir / "schema.json").exists())
            self.assertEqual(1, len(list(dataset_dir.glob("schema.json"))))
            self.assertEqual(2, len(list(dataset_dir.glob("*.metadata.json"))))

    def test_shared_schemas_define_standard_and_usda_layouts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_sample_csv(root / "processed" / "snap" / "baseline_2024-06.csv")
            _write_usda_sample_csv(
                root / "processed" / "usda_farm_programs" / "baseline_2026-02.csv"
            )

            _generate(root)
            standard = json.loads(
                (root / "schemas" / "baseline_detail.schema.json").read_text(encoding="utf-8")
            )
            usda = json.loads(
                (root / "schemas" / "usda_baseline_detail.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            for meta in schema.CORE_COLUMN_META:
                self.assertIn(meta["name"], standard["required"])
            for meta in schema.USDA_COLUMN_META:
                self.assertNotIn(meta["name"], standard["required"])
                self.assertIn(meta["name"], usda["required"])

            usda_dataset_schema = json.loads(
                (
                    root
                    / "processed"
                    / "usda_farm_programs"
                    / "schema.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual("usda_baseline_detail", usda_dataset_schema["x-cbo"]["schema_family"])

    def test_release_metadata_contains_provenance_coverage_and_totals_warning(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            release = root / "processed" / "snap" / "baseline_2024-06.csv"
            _write_sample_csv(release)
            _generate(root)

            metadata = json.loads(release.with_suffix(".metadata.json").read_text(encoding="utf-8"))
            self.assertEqual("2024-06", metadata["vintage"])
            self.assertEqual(2, metadata["row_count"])
            self.assertEqual(["51312-2024-06-snap.xlsx"], metadata["source_files"])
            self.assertEqual({"start_year": 2024, "end_year": 2024}, metadata["period_coverage"])
            self.assertTrue(metadata["contains_totals"])
            self.assertIn("double-counting", metadata["aggregation_note"])
            self.assertEqual(64, len(metadata["sha256"]))

    def test_superscript_notes_live_in_release_metadata_not_stable_schema(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            processed = root / "processed" / "snap"
            raw = root / "raw"
            raw.mkdir()
            release = processed / "baseline_2024-06.csv"
            _write_sample_csv(release, has_totals=False)

            workbook = Workbook()
            worksheet = workbook.active
            worksheet.title = "SNAP_06-2024"
            worksheet["A10"] = CellRichText(
                [
                    "Estimated Budget Authority",
                    TextBlock(InlineFont(vertAlign="superscript"), "a"),
                ]
            )
            worksheet["D10"] = 103764
            worksheet["A12"] = "a. Includes a source-specific adjustment."
            workbook.save(raw / "51312-2024-06-snap.xlsx")

            self.assertEqual(0, _generate(root, raw_dir=raw))
            metadata = json.loads(release.with_suffix(".metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(1, len(metadata["annotations"]))
            self.assertEqual("a", metadata["annotations"][0]["marker"])
            self.assertIn("source-specific adjustment", metadata["annotations"][0]["variable_note"])

            dataset_schema = (processed / "schema.json").read_text(encoding="utf-8")
            self.assertNotIn("source-specific adjustment", dataset_schema)
            self.assertNotIn('"annotations"', dataset_schema)

    def test_annotation_audit_fails_when_note_text_is_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            processed = root / "processed" / "snap"
            raw = root / "raw"
            raw.mkdir()
            _write_sample_csv(processed / "baseline_2024-06.csv", has_totals=False)

            workbook = Workbook()
            worksheet = workbook.active
            worksheet.title = "SNAP_06-2024"
            worksheet["A10"] = CellRichText(
                [
                    "Estimated Budget Authority",
                    TextBlock(InlineFont(vertAlign="superscript"), "a"),
                ]
            )
            worksheet["D10"] = 103764
            workbook.save(raw / "51312-2024-06-snap.xlsx")

            self.assertEqual(1, _generate(root, raw_dir=raw))

    def test_catalog_indexes_logical_datasets_and_releases(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            dataset_dir = root / "processed" / "snap"
            _write_sample_csv(dataset_dir / "baseline_2024-06.csv")
            _write_sample_csv(
                dataset_dir / "baseline_2026-02.csv",
                source_file="51312-2026-02-snap.xlsx",
                source_sheet="SNAP_02-2026",
                year=2026,
            )
            _generate(root)

            catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
            self.assertEqual(1, len(catalog["datasets"]))
            self.assertEqual("snap", catalog["datasets"][0]["dataset"])
            self.assertEqual(2, len(catalog["datasets"][0]["releases"]))
            self.assertEqual("2026-02", catalog["datasets"][0]["releases"][0]["vintage"])

    def test_noncanonical_release_location_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_sample_csv(root / "processed" / "baseline_2024-06.csv")
            with self.assertRaisesRegex(ValueError, "canonical dataset directory"):
                _generate(root)

    def test_generate_schemas_returns_1_when_no_csvs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.assertEqual(1, _generate(root))


if __name__ == "__main__":
    unittest.main()
