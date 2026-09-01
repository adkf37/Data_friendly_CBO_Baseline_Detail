import tempfile
import unittest
from pathlib import Path

from etl import config
from etl import transform


class ConfigTests(unittest.TestCase):
    def test_dataset_registry_has_unique_program_ids(self):
        self.assertEqual(30, len(config.DATASETS))
        self.assertEqual(30, len(config.DATASETS_BY_PROGRAM_ID))
        self.assertEqual("USDA Farm Programs", config.DATASETS["usda_farm_programs"].title)
        self.assertEqual(
            "usda_baseline_detail",
            config.DATASETS["usda_farm_programs"].schema_family,
        )

    def test_split_parse_plans_preserve_all_workbooks(self):
        files = config.iter_parse_plan_files(config.PARSE_PLANS_DIR)
        plans = transform._read_plan(config.PARSE_PLANS_DIR)
        self.assertEqual(30, len(files))
        self.assertEqual(246, len({plan.workbook for plan in plans}))

    def test_registered_output_uses_dataset_directory_and_vintage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = config.get_output_path(
                Path(tmpdir),
                workbook="51317-2026-02-usda.xlsx",
                output_dataset="usda_2026_02",
            )
            self.assertEqual(
                Path(tmpdir) / "usda_farm_programs" / "baseline_2026-02.csv",
                output,
            )

    def test_ad_hoc_output_without_vintage_retains_flat_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = config.get_output_path(
                Path(tmpdir),
                workbook="51293-2026-02-childnutrition.xlsx",
                output_dataset="custom_test_dataset",
            )
            self.assertEqual(Path(tmpdir) / "custom_test_dataset.csv", output)


if __name__ == "__main__":
    unittest.main()
