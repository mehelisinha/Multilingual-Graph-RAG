#!/usr/bin/env python3
"""Build a multilingual JSONL corpus directly from EUR-Lex (Cellar API).

Alternative to download_multieurlex.py for networks where the HuggingFace CDN
is blocked. Discovers CELEX ids of EU regulations via the Cellar SPARQL
endpoint, downloads each document's XHTML manifestation per language, strips
the markup, and writes the same JSONL record shape that ingest_to_milvus.py,
build_graph.py and validate_data.py consume:

    {"document_id", "celex_id", "language", "title", "text"}

Everything goes over plain HTTP against publications.europa.eu — free, no API
key, no scraping of the eur-lex.europa.eu website (which is bot-protected).
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "data" / "raw" / "multieurlex"

SPARQL_URL = "http://publications.europa.eu/webapi/rdf/sparql"
CELLAR_URL = "http://publications.europa.eu/resource/celex/{celex}"
LANGUAGES = ("de", "en", "fr", "pl")
REQUEST_DELAY_SECONDS = 0.2
MIN_TEXT_CHARS = 500

# Regulations with a plain CELEX id (sector 3, type R), excluding corrigenda
# like 32024R1689R(03) whose manifestations are tiny correction notices.
SPARQL_QUERY = """\
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT DISTINCT ?celex WHERE {{
  ?work cdm:resource_legal_id_celex ?celex .
  ?work cdm:work_has_resource-type <http://publications.europa.eu/resource/authority/resource-type/REG> .
  FILTER(REGEX(?celex, '^3[0-9]{{4}}R[0-9]{{4}}$'))
}}
ORDER BY DESC(?celex)
LIMIT {limit}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download EUR-Lex corpus via Cellar")
    parser.add_argument(
        "--sample",
        type=int,
        default=1000,
        help="Target number of records, documents x languages (default: 1000)",
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        default=list(LANGUAGES),
        help="Language codes to export (default: de en fr pl)",
    )
    return parser.parse_args()


class _TextExtractor(HTMLParser):
    """Strip tags from a Cellar XHTML manifestation, keeping block structure."""

    _SKIP = {"script", "style", "head"}
    _BLOCK = {"p", "div", "table", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.title: str = ""
        self._skip_depth = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._SKIP:
            self._skip_depth += 1
        elif tag == "title":
            self._in_title = True
        elif tag in self._BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP and self._skip_depth:
            self._skip_depth -= 1
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        elif not self._skip_depth:
            self.parts.append(data)


def html_to_text(html: str) -> tuple[str, str]:
    extractor = _TextExtractor()
    extractor.feed(html)
    text = "".join(extractor.parts)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip(), extractor.title.strip()


def http_get(url: str, headers: dict[str, str]) -> bytes | None:
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        if exc.code in (404, 406, 300):
            return None
        raise


def discover_celex_ids(limit: int) -> list[str]:
    query = SPARQL_QUERY.format(limit=limit)
    url = (
        f"{SPARQL_URL}?query={urllib.parse.quote(query)}"
        "&format=application%2Fsparql-results%2Bjson"
    )
    body = http_get(url, {"User-Agent": "multilingual-graph-rag/0.1"})
    if body is None:
        raise SystemExit("SPARQL query failed")
    results = json.loads(body)
    return [b["celex"]["value"] for b in results["results"]["bindings"]]


def fetch_document(celex: str, language: str) -> tuple[str, str] | None:
    body = http_get(
        CELLAR_URL.format(celex=celex),
        {
            "Accept": "application/xhtml+xml",
            "Accept-Language": language,
            "User-Agent": "multilingual-graph-rag/0.1",
        },
    )
    if body is None:
        return None
    text, title = html_to_text(body.decode("utf-8", errors="replace"))
    if len(text) < MIN_TEXT_CHARS:
        return None
    return text, title or f"CELEX {celex}"


def main() -> None:
    args = parse_args()
    docs_needed = max(1, args.sample // len(args.languages))
    # Over-fetch ids: not every regulation exists in every language.
    celex_ids = discover_celex_ids(docs_needed * 3)
    print(f"Discovered {len(celex_ids)} CELEX ids, targeting {args.sample} records")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"sample_{args.sample}.jsonl"

    written = 0
    with output_path.open("w", encoding="utf-8") as handle:
        for celex in celex_ids:
            if written >= args.sample:
                break
            for language in args.languages:
                if written >= args.sample:
                    break
                try:
                    fetched = fetch_document(celex, language)
                except (urllib.error.URLError, TimeoutError) as exc:
                    print(f"WARN {celex} [{language}]: {exc}")
                    continue
                if fetched is None:
                    continue
                text, title = fetched
                handle.write(
                    json.dumps(
                        {
                            "document_id": f"{celex}_{language}",
                            "celex_id": celex,
                            "language": language,
                            "title": title,
                            "text": text,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                written += 1
                if written % 50 == 0:
                    print(f"  {written}/{args.sample} records")
                time.sleep(REQUEST_DELAY_SECONDS)

    print(f"Wrote {written} records to {output_path}")


if __name__ == "__main__":
    main()
