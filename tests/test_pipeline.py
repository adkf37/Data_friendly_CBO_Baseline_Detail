"""Tests for run_pipeline.py — pipeline runner entrypoint."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_step_fn(exit_code: int = 0):
    """Return a callable that records calls and returns exit_code."""
    fn = MagicMock(return_value=exit_code)
    return fn


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class PipelineRunStepTests(unittest.TestCase):
    """Unit tests for _run_step."""

    def _import_run_step(self):
        # Ensure repo root is on sys.path for import
        repo_root = str(Path(__file__).resolve().parent.parent)
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        from run_pipeline import _run_step
        return _run_step

    def test_run_step_returns_true_on_success(self):
        _run_step = self._import_run_step()
        fn = _make_step_fn(exit_code=0)
        result = _run_step("test-step", fn)
        self.assertTrue(result)
        fn.assert_called_once()

    def test_run_step_returns_false_on_nonzero_exit(self):
        _run_step = self._import_run_step()
        fn = _make_step_fn(exit_code=1)
        result = _run_step("test-step", fn)
        self.assertFalse(result)

    def test_run_step_returns_false_on_exception(self):
        _run_step = self._import_run_step()
        fn = MagicMock(side_effect=RuntimeError("boom"))
        result = _run_step("test-step", fn)
        self.assertFalse(result)


class PipelineMainTests(unittest.TestCase):
    """Integration-level tests for the pipeline main() function."""

    def _import_main(self):
        repo_root = str(Path(__file__).resolve().parent.parent)
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        import run_pipeline as rp
        return rp

    def test_main_single_step_calls_only_that_step(self):
        rp = self._import_main()
        called = []
        step_fns = {name: MagicMock(return_value=0, side_effect=lambda _n=name: called.append(_n) or 0)
                    for name in rp.STEP_NAMES}

        with patch("run_pipeline._import_steps", return_value=step_fns), \
             patch("sys.argv", ["run_pipeline.py", "--step", "schema"]):
            rc = rp.main()

        self.assertEqual(0, rc)
        self.assertEqual(["schema"], called)

    def test_main_stops_on_first_failure(self):
        rp = self._import_main()
        called = []

        def _step(name):
            def _fn():
                called.append(name)
                return 1 if name == "inspect" else 0
            return _fn

        step_fns = {name: _step(name) for name in rp.STEP_NAMES}

        with patch("run_pipeline._import_steps", return_value=step_fns), \
             patch("sys.argv", ["run_pipeline.py"]):
            rc = rp.main()

        self.assertEqual(1, rc)
        # Should stop after inspect, not run transform/schema/verify
        self.assertIn("download", called)
        self.assertIn("inspect", called)
        self.assertNotIn("transform", called)

    def test_main_full_run_passes_all_steps(self):
        rp = self._import_main()
        step_fns = {name: MagicMock(return_value=0) for name in rp.STEP_NAMES}

        with patch("run_pipeline._import_steps", return_value=step_fns), \
             patch("sys.argv", ["run_pipeline.py"]):
            rc = rp.main()

        self.assertEqual(0, rc)
        for fn in step_fns.values():
            fn.assert_called_once()


class ReadmeContentsTests(unittest.TestCase):
    """Assert README.md contains the required sections and canonical command."""

    def setUp(self):
        self.readme_path = Path(__file__).resolve().parent.parent / "README.md"

    def test_readme_exists(self):
        self.assertTrue(self.readme_path.exists(), "README.md should exist at repo root")

    def test_readme_contains_canonical_command(self):
        content = self.readme_path.read_text(encoding="utf-8")
        self.assertIn("python run_pipeline.py", content)

    def test_readme_contains_prerequisites(self):
        content = self.readme_path.read_text(encoding="utf-8")
        self.assertIn("Prerequisites", content)

    def test_readme_contains_install_steps(self):
        content = self.readme_path.read_text(encoding="utf-8")
        self.assertIn("pip install", content)

    def test_readme_contains_quick_start(self):
        content = self.readme_path.read_text(encoding="utf-8")
        self.assertIn("Quick Start", content)

    def test_readme_contains_output_locations(self):
        content = self.readme_path.read_text(encoding="utf-8")
        self.assertIn("data/processed", content)
        self.assertIn("docs/schemas", content)

    def test_readme_contains_schema_link(self):
        content = self.readme_path.read_text(encoding="utf-8")
        self.assertIn("docs/schemas/README.md", content)

    def test_readme_contains_cbo_attribution(self):
        content = self.readme_path.read_text(encoding="utf-8")
        # Must mention CBO / Congressional Budget Office
        self.assertIn("Congressional Budget Office", content)


if __name__ == "__main__":
    unittest.main()
