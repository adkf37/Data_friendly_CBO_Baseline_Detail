import json
import io
import tempfile
import unittest
import zipfile
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from src import download


def xlsx_bytes(label="workbook"):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as workbook:
        workbook.writestr("[Content_Types].xml", "<Types />")
        workbook.writestr("xl/workbook.xml", f"<workbook>{label}</workbook>")
    return buffer.getvalue()


class DummyResponse:
    def __init__(self, text="", content=b"", status_code=200, headers=None):
        self.text = text
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise download.requests.HTTPError(f"status={self.status_code}")


class DummySession:
    def __init__(self, responses_by_url):
        self.responses_by_url = responses_by_url
        self.timeouts = []
        self.request_headers = []
        self.headers = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def get(self, url, timeout=None, **kwargs):
        self.timeouts.append(timeout)
        self.request_headers.append(kwargs.get("headers", {}))
        value = self.responses_by_url[url]
        if isinstance(value, list):
            value = value.pop(0)
        if isinstance(value, Exception):
            raise value
        return value


class DownloadTests(unittest.TestCase):
    def test_direct_script_help_does_not_shadow_standard_inspect_module(self):
        repo_root = Path(__file__).resolve().parent.parent
        result = subprocess.run(
            [sys.executable, str(repo_root / "src" / "download.py"), "--help"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("usage:", result.stdout.lower())

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

    def test_discover_workbooks_accepts_current_cbo_folder_date_mismatches(self):
        html = """
        <a href="/system/files/2026-01/51317-2026-02-usda.xlsx">USDA Feb 2026</a>
        <a href="/system/files/2026-01/51312-2026-02-snap.xlsx">SNAP Feb 2026</a>
        <a href="/system/files/2026-05/51310-2026-02-studentloan.xlsx">Student Loan Feb 2026</a>
        <a href="/system/files/2026-06/51300-2026-06-highwaytrustfund.xlsx">Highway Jun 2026</a>
        """
        links = download.discover_workbooks(html)
        self.assertEqual(
            [
                "51317-2026-02-usda.xlsx",
                "51312-2026-02-snap.xlsx",
                "51310-2026-02-studentloan.xlsx",
                "51300-2026-06-highwaytrustfund.xlsx",
            ],
            [item.filename for item in links],
        )

    def test_run_download_writes_manifest_with_required_fields(self):
        html = '<a href="/files/2026/health.xlsx">Health</a>'
        workbook_content = xlsx_bytes()

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
            self.assertTrue(entry["active_on_index"])
            self.assertEqual(entry["discovered_at"], entry["checked_at"])

    def test_run_download_refreshes_existing_file_when_remote_content_changes(self):
        html = '<a href="/files/2026/health.xlsx">Health</a>'
        old_content = xlsx_bytes("old")
        new_content = xlsx_bytes("corrected")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            destination = output_dir / "health.xlsx"
            destination.write_bytes(old_content)
            (output_dir / "manifest.json").write_text(
                json.dumps(
                    [
                        {
                            "filename": "health.xlsx",
                            "source_url": "https://example.test/files/2026/health.xlsx",
                            "downloaded_at": "2026-02-01T00:00:00Z",
                            "etag": '"old"',
                        }
                    ]
                ),
                encoding="utf-8",
            )
            dummy = DummySession(
                {
                    "https://example.test/index": DummyResponse(text=html),
                    "https://example.test/files/2026/health.xlsx": DummyResponse(
                        content=new_content,
                        headers={"ETag": '"new"', "Last-Modified": "Wed, 11 Feb 2026 12:00:00 GMT"},
                    ),
                }
            )

            with patch.object(download.requests, "Session", return_value=dummy):
                download.run_download(
                    index_url="https://example.test/index",
                    output_dir=output_dir,
                    timeout=1,
                    retries=0,
                )

            self.assertEqual(new_content, destination.read_bytes())
            self.assertEqual({'If-None-Match': '"old"'}, dummy.request_headers[1])
            entry = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))[0]
            self.assertEqual('"new"', entry["etag"])
            self.assertEqual("Wed, 11 Feb 2026 12:00:00 GMT", entry["last_modified"])
            self.assertNotEqual("2026-02-01T00:00:00Z", entry["downloaded_at"])

    def test_run_download_retains_manifest_entries_no_longer_on_current_index(self):
        html = '<a href="/files/2026/health.xlsx">Health</a>'
        current_content = xlsx_bytes("health")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            (output_dir / "manifest.json").write_text(
                json.dumps(
                    [
                        {
                            "filename": "historical.xlsx",
                            "source_url": "https://example.test/files/2020/historical.xlsx",
                            "downloaded_at": "2020-01-01T00:00:00Z",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            dummy = DummySession(
                {
                    "https://example.test/index": DummyResponse(text=html),
                    "https://example.test/files/2026/health.xlsx": DummyResponse(content=current_content),
                }
            )

            with patch.object(download.requests, "Session", return_value=dummy):
                download.run_download(
                    index_url="https://example.test/index",
                    output_dir=output_dir,
                    timeout=1,
                    retries=0,
                )

            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            by_filename = {entry["filename"]: entry for entry in manifest}
            self.assertEqual({"health.xlsx", "historical.xlsx"}, set(by_filename))
            self.assertFalse(by_filename["historical.xlsx"]["active_on_index"])

    def test_run_download_rejects_datadome_challenge_with_clear_error(self):
        challenge = DummyResponse(
            text="Please enable JS",
            content=b"Please enable JS <script src='captcha-delivery.com/c.js'></script>",
            status_code=403,
            headers={"X-DataDome": "protected"},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            dummy = DummySession({"https://example.test/index": challenge})
            with patch.object(download.requests, "Session", return_value=dummy):
                with self.assertRaisesRegex(download.DownloadError, "DataDome"):
                    download.run_download(
                        index_url="https://example.test/index",
                        output_dir=Path(tmpdir),
                        timeout=1,
                        retries=2,
                    )
            self.assertEqual(1, len(dummy.timeouts))

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
