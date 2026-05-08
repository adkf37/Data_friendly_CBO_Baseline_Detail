from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

INDEX_URL = "https://www.cbo.gov/data/baseline-projections-selected-programs"


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


def fetch_with_retries(session: requests.Session, url: str, timeout: float, retries: int) -> requests.Response:
    last_exception: Exception | None = None
    for attempt in range(retries + 1):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last_exception = exc
            if attempt == retries:
                break
    raise DownloadError(f"Failed to fetch {url}: {last_exception}") from last_exception


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def write_manifest(path: Path, entries: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(list(entries), indent=2) + "\n", encoding="utf-8")


def run_download(
    index_url: str = INDEX_URL,
    output_dir: Path = Path("data/raw"),
    timeout: float = 20.0,
    retries: int = 2,
    force: bool = False,
) -> int:
    """Download discovered workbooks and write manifest metadata.

    Manifest `downloaded_at` is an ISO timestamp for files downloaded in the
    current run and `None` for files skipped because they already existed.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    discovered_at = utc_now_iso()
    downloaded = 0
    skipped = 0
    manifest_entries: list[dict] = []

    with requests.Session() as session:
        response = fetch_with_retries(session, index_url, timeout=timeout, retries=retries)
        links = discover_workbooks(response.text, base_url=index_url)
        print(f"Discovered {len(links)} workbook(s).")

        if not links:
            raise DownloadError(f"No Excel links found at {index_url}")

        for link in links:
            destination = output_dir / link.filename
            downloaded_at = None
            action = "skip"

            if destination.exists() and not force:
                skipped += 1
            else:
                workbook_response = fetch_with_retries(session, link.source_url, timeout=timeout, retries=retries)
                destination.write_bytes(workbook_response.content)
                downloaded += 1
                action = "download"
                downloaded_at = utc_now_iso()

            content = destination.read_bytes()
            entry = {
                "program_slug": link.program_slug,
                "filename": link.filename,
                "source_url": link.source_url,
                "discovered_at": discovered_at,
                "downloaded_at": downloaded_at,
                "sha256": sha256_bytes(content),
                "bytes": len(content),
            }
            manifest_entries.append(entry)
            print(f"{action.upper()}: {link.filename}")

    write_manifest(output_dir / "manifest.json", manifest_entries)
    print(f"Completed. downloaded={downloaded}, skipped={skipped}, manifest={output_dir / 'manifest.json'}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download CBO baseline Excel workbooks and create a manifest.")
    parser.add_argument("--force", action="store_true", help="Re-download files even when they already exist")
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
        )
    except DownloadError as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
