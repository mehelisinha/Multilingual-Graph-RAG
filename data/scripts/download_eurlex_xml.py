#!/usr/bin/env python3
"""Download EUR-Lex Formex XML documents from the Publications Office Cellar API.

Cellar serves every EUR-Lex document at a stable URL keyed by CELEX id:
    http://publications.europa.eu/resource/celex/{CELEX_ID}
Content negotiation (Accept header + Accept-Language) selects the Formex XML
manifestation. Free, no API key, no rate-limit registration required.

CELEX ids are taken either from --celex arguments or from a previously
downloaded MultiEURLEX JSONL sample (see download_multieurlex.py).
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT / "data" / "raw" / "multieurlex"
OUTPUT_DIR = ROOT / "data" / "raw" / "eurlex_xml"

CELLAR_URL = "http://publications.europa.eu/resource/celex/{celex}"
ACCEPT_XML = "application/xml; notice=branch"
LANGUAGES = ("de", "en", "fr", "pl")
REQUEST_DELAY_SECONDS = 0.5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download EUR-Lex XML via Cellar")
    parser.add_argument(
        "--celex",
        nargs="+",
        default=None,
        help="Explicit CELEX ids to download (default: ids from MultiEURLEX sample)",
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        default=list(LANGUAGES),
        help="Language codes to request (default: de en fr pl)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum documents to download (default: 50)",
    )
    return parser.parse_args()


def celex_ids_from_sample(limit: int) -> list[str]:
    candidates = sorted(INPUT_DIR.glob("sample_*.jsonl"), reverse=True)
    if not candidates:
        raise SystemExit(
            f"No JSONL found in {INPUT_DIR} and no --celex given. "
            "Run download_multieurlex.py first."
        )
    ids: list[str] = []
    seen: set[str] = set()
    with candidates[0].open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            celex = str(json.loads(line).get("celex_id", "")).strip()
            if celex and celex not in seen:
                seen.add(celex)
                ids.append(celex)
            if len(ids) >= limit:
                break
    return ids


def fetch(celex: str, language: str) -> bytes | None:
    request = urllib.request.Request(
        CELLAR_URL.format(celex=celex),
        headers={
            "Accept": ACCEPT_XML,
            "Accept-Language": language,
            "User-Agent": "multilingual-graph-rag/0.1 (data pipeline)",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def main() -> None:
    args = parse_args()
    celex_ids = args.celex or celex_ids_from_sample(args.limit)
    celex_ids = celex_ids[: args.limit]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    skipped = 0
    for celex in celex_ids:
        for language in args.languages:
            output_path = OUTPUT_DIR / f"{celex}_{language}.xml"
            if output_path.exists():
                skipped += 1
                continue
            try:
                body = fetch(celex, language)
            except (urllib.error.URLError, TimeoutError) as exc:
                print(f"WARN {celex} [{language}]: {exc}")
                continue
            if body is None:
                skipped += 1
                continue
            output_path.write_bytes(body)
            downloaded += 1
            time.sleep(REQUEST_DELAY_SECONDS)

    print(f"Downloaded {downloaded} XML files to {OUTPUT_DIR} ({skipped} skipped)")


if __name__ == "__main__":
    main()
