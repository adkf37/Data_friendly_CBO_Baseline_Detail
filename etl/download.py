from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path

if sys.path:
    script_dir = Path(__file__).resolve().parent
    if Path(sys.path[0]).resolve() == script_dir:
        sys.path[0] = str(script_dir.parent)

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Mapping
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

INDEX_URL = "https://www.cbo.gov/data/baseline-projections-selected-programs"
DEFAULT_HEADERS = {
    "User-Agent": (
        "CBO-Baseline-Detail-Downloader/1.0 "
        "(+https://github.com/adkf37/Data_friendly_CBO_Baseline_Detail)"
    ),
    "Accept": "text/html,application/xhtml+xml,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*;q=0.8",
}
XLSX_REQUIRED_MEMBERS = {"[Content_Types].xml", "xl/workbook.xml"}


class DownloadError(RuntimeError):
    """Raised when workbook discovery or download fails."""


@dataclass(frozen=True)
class WorkbookLink:
    source_url: str
    filename: str
    program_slug: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def extract_xlsx_filename(source_url: str) -> str | None:
    path = urlparse(source_url).path
    filename = Path(path).name
    if not filename:
        return None
    if not filename.lower().endswith(".xlsx"):
        return None
    return filename


def program_slug_from_filename(filename: str) -> str:
    stem = Path(filename).stem.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    return slug or "program"


def discover_workbooks(html: str, base_url: str = INDEX_URL) -> list[WorkbookLink]:
    soup = BeautifulSoup(html, "lxml")
    links: list[WorkbookLink] = []
    seen: set[str] = set()

    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "").strip()
        if not href:
            continue
        absolute_url = urljoin(base_url, href)
        filename = extract_xlsx_filename(absolute_url)
        if not filename:
            continue
        if absolute_url in seen:
            continue
        seen.add(absolute_url)
        links.append(
            WorkbookLink(
                source_url=absolute_url,
                filename=filename,
                program_slug=program_slug_from_filename(filename),
            )
        )

    return links


def is_datadome_challenge(response: requests.Response) -> bool:
    """Return whether CBO served its JavaScript/CAPTCHA challenge page."""
    if response.status_code != 403:
        return False
    if response.headers.get("X-DataDome", "").lower() == "protected":
        return True
    return b"captcha-delivery.com" in response.content or b"Please enable JS" in response.content


def fetch_with_retries(
    session: requests.Session,
    url: str,
    timeout: float,
    retries: int,
    headers: Mapping[str, str] | None = None,
) -> requests.Response:
    last_exception: Exception | None = None
    for attempt in range(retries + 1):
        try:
            response = session.get(url, timeout=timeout, headers=dict(headers or {}))
            if is_datadome_challenge(response):
                raise DownloadError(
                    "CBO served a DataDome JavaScript/CAPTCHA challenge for "
                    f"{url}. Run from a network permitted by cbo.gov; the downloader "
                    "does not attempt to bypass access controls."
                )
            response.raise_for_status()
            return response
        except DownloadError:
            raise
        except requests.RequestException as exc:
            last_exception = exc
            if attempt == retries:
                break
    raise DownloadError(f"Failed to fetch {url}: {last_exception}") from last_exception


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def validate_xlsx_bytes(content: bytes, source_url: str) -> None:
    """Reject HTML error pages and other non-XLSX responses before writing."""
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as workbook:
            missing = XLSX_REQUIRED_MEMBERS.difference(workbook.namelist())
    except (zipfile.BadZipFile, OSError) as exc:
        raise DownloadError(f"Downloaded content is not a valid XLSX workbook: {source_url}") from exc
    if missing:
        raise DownloadError(
            f"Downloaded archive is missing required XLSX members {sorted(missing)}: {source_url}"
        )


def write_manifest(path: Path, entries: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(list(entries), indent=2) + "\n", encoding="utf-8")


def load_manifest(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        entries = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise DownloadError(f"Could not read existing manifest {path}: {exc}") from exc
    if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
        raise DownloadError(f"Existing manifest must contain a JSON list of objects: {path}")
    return entries


def conditional_headers(entry: Mapping[str, object] | None) -> dict[str, str]:
    headers: dict[str, str] = {}
    if not entry:
        return headers
    etag = entry.get("etag")
    last_modified = entry.get("last_modified")
    if isinstance(etag, str) and etag:
        headers["If-None-Match"] = etag
    if isinstance(last_modified, str) and last_modified:
        headers["If-Modified-Since"] = last_modified
    return headers


def run_download(
    index_url: str = INDEX_URL,
    output_dir: Path = Path("data/raw"),
    timeout: float = 20.0,
    retries: int = 2,
    force: bool = False,
    refresh_existing: bool = True,
) -> int:
    """Download all linked workbooks and write cumulative manifest metadata.

    Existing files are checked by default because CBO sometimes republishes a
    corrected workbook at the same URL. Conditional request headers are used
    when the existing manifest has validators; otherwise the remote content is
    hashed and the local file is rewritten only when it changed.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    discovered_at = utc_now_iso()
    added = 0
    updated = 0
    unchanged = 0
    skipped = 0
    manifest_entries: list[dict] = []
    manifest_path = output_dir / "manifest.json"
    previous_entries = load_manifest(manifest_path)
    previous_by_filename = {
        entry["filename"]: entry
        for entry in previous_entries
        if isinstance(entry.get("filename"), str)
    }

    with requests.Session() as session:
        session.headers.update(DEFAULT_HEADERS)
        response = fetch_with_retries(session, index_url, timeout=timeout, retries=retries)
        links = discover_workbooks(response.text, base_url=index_url)
        print(f"Discovered {len(links)} workbook(s).")

        if not links:
            raise DownloadError(f"No Excel links found at {index_url}")

        live_by_filename: dict[str, WorkbookLink] = {}
        for link in links:
            previous_link = live_by_filename.get(link.filename)
            if previous_link and previous_link.source_url != link.source_url:
                raise DownloadError(
                    f"The index maps {link.filename} to multiple URLs: "
                    f"{previous_link.source_url} and {link.source_url}"
                )
            live_by_filename[link.filename] = link

        for link in live_by_filename.values():
            destination = output_dir / link.filename
            previous_entry = previous_by_filename.get(link.filename)
            downloaded_at = previous_entry.get("downloaded_at") if previous_entry else None
            checked_at = previous_entry.get("checked_at") if previous_entry else None
            etag = previous_entry.get("etag") if previous_entry else None
            last_modified = previous_entry.get("last_modified") if previous_entry else None

            if destination.exists() and not (force or refresh_existing):
                skipped += 1
                action = "skip"
                content = destination.read_bytes()
            else:
                request_headers = (
                    conditional_headers(previous_entry)
                    if destination.exists() and not force
                    else {}
                )
                workbook_response = fetch_with_retries(
                    session,
                    link.source_url,
                    timeout=timeout,
                    retries=retries,
                    headers=request_headers,
                )
                checked_at = discovered_at
                if workbook_response.status_code == 304:
                    if not destination.exists():
                        raise DownloadError(f"CBO returned 304 but no local file exists: {destination}")
                    content = destination.read_bytes()
                    unchanged += 1
                    action = "unchanged"
                else:
                    remote_content = workbook_response.content
                    validate_xlsx_bytes(remote_content, link.source_url)
                    local_content = destination.read_bytes() if destination.exists() else None
                    if local_content == remote_content and not force:
                        content = local_content
                        unchanged += 1
                        action = "unchanged"
                    else:
                        destination.write_bytes(remote_content)
                        content = remote_content
                        downloaded_at = discovered_at
                        if local_content is None:
                            added += 1
                            action = "add"
                        else:
                            updated += 1
                            action = "update"
                    etag = workbook_response.headers.get("ETag")
                    last_modified = workbook_response.headers.get("Last-Modified")

            entry = {
                "program_slug": link.program_slug,
                "filename": link.filename,
                "source_url": link.source_url,
                "discovered_at": discovered_at,
                "downloaded_at": downloaded_at,
                "checked_at": checked_at,
                "last_seen_at": discovered_at,
                "active_on_index": True,
                "sha256": sha256_bytes(content),
                "bytes": len(content),
            }
            if etag:
                entry["etag"] = etag
            if last_modified:
                entry["last_modified"] = last_modified
            manifest_entries.append(entry)
            print(f"{action.upper()}: {link.filename}")

    live_filenames = set(live_by_filename)
    for previous_entry in previous_entries:
        if previous_entry.get("filename") in live_filenames:
            continue
        retained_entry = dict(previous_entry)
        retained_entry["active_on_index"] = False
        manifest_entries.append(retained_entry)

    write_manifest(manifest_path, manifest_entries)
    print(
        "Completed. "
        f"added={added}, updated={updated}, unchanged={unchanged}, skipped={skipped}, "
        f"manifest={manifest_path}"
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download CBO baseline Excel workbooks and create a manifest.")
    parser.add_argument("--force", action="store_true", help="Rewrite files even when remote content is unchanged")
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Do not check existing files for same-URL CBO corrections (faster, but may leave stale data)",
    )
    parser.add_argument("--timeout", type=float, default=20.0, help="Request timeout in seconds")
    parser.add_argument("--retries", type=int, default=2, help="Number of retries after initial request failure")
    parser.add_argument("--index-url", default=INDEX_URL, help="Index URL to scrape for workbook links")
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw"), help="Directory for downloaded workbooks")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return run_download(
            index_url=args.index_url,
            output_dir=args.output_dir,
            timeout=args.timeout,
            retries=args.retries,
            force=args.force,
            refresh_existing=not args.skip_existing,
        )
    except DownloadError as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
