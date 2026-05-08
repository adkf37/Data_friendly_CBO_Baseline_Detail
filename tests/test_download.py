import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import download


class DummyResponse:
    def __init__(self, text="", content=b"", status_code=200):
        self.text = text
        self.content = content
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise download.requests.HTTPError(f"status={self.status_code}")


class DummySession:
    def __init__(self, responses_by_url):
        self.responses_by_url = responses_by_url
        self.timeouts = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def get(self, url, timeout=None, **kwargs):
        self.timeouts.append(timeout)
        value = self.responses_by_url[url]
        if isinstance(value, Exception):
            raise value
        return value


class DownloadTests(unittest.TestCase):
    def test_discover_workbooks_ignores_pdf_links(self):
        html = """
        <html><body>
            <a href="/files/2026/health.xlsx">Health</a>
            <a href="/files/2026/health.pdf">PDF</a>
            <a href="https://www.cbo.gov/files/2026/income.xlsx?download=1">Income</a>
        </body></html>
        """
        links = download.discover_workbooks(html)
        self.assertEqual(["health.xlsx", "income.xlsx"], [item.filename for item in links])

    def test_run_download_writes_manifest_with_required_fields(self):
        html = '<a href="/files/2026/health.xlsx">Health</a>'
        workbook_content = b"xlsx-content"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            dummy = DummySession(
                {
                    "https://example.test/index": DummyResponse(text=html),
                    "https://example.test/files/2026/health.xlsx": DummyResponse(content=workbook_content),
                }
            )

            with patch.object(download.requests, "Session", return_value=dummy):
                rc = download.run_download(
                    index_url="https://example.test/index",
                    output_dir=output_dir,
                    timeout=1,
                    retries=0,
                    force=False,
                )

            self.assertEqual(0, rc)
            self.assertEqual([1, 1], dummy.timeouts)
            self.assertTrue((output_dir / "health.xlsx").exists())

            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(1, len(manifest))
            entry = manifest[0]
            required = {
                "program_slug",
                "filename",
                "source_url",
                "discovered_at",
                "downloaded_at",
                "sha256",
                "bytes",
            }
            self.assertTrue(required.issubset(entry.keys()))
            self.assertEqual("health.xlsx", entry["filename"])
            self.assertEqual(len(workbook_content), entry["bytes"])

    def test_run_download_errors_when_no_excel_links(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dummy = DummySession({"https://example.test/index": DummyResponse(text="<a href='/x.pdf'>pdf</a>")})

            with patch.object(download.requests, "Session", return_value=dummy):
                with self.assertRaises(download.DownloadError):
                    download.run_download(
                        index_url="https://example.test/index",
                        output_dir=Path(tmpdir),
                        timeout=1,
                        retries=0,
                    )


if __name__ == "__main__":
    unittest.main()
