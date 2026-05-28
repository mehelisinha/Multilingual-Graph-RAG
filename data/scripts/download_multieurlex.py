#!/usr/bin/env python3
"""Download MultiEURLEX samples from HuggingFace into data/raw/multieurlex."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

OUTPUT_DIR = ROOT / "data" / "raw" / "multieurlex"
LANGUAGES = ("de", "en", "fr", "pl")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download MultiEURLEX sample records")
    parser.add_argument(
        "--sample",
        type=int,
        default=1000,
        help="Maximum records to download (default: 1000)",
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        default=list(LANGUAGES),
        help="Language codes to export (default: de en fr pl)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise SystemExit("Install dev deps: pip install -r backend/requirements-dev.txt") from exc

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dataset = load_dataset("multi_eurlex", "all", split="train", streaming=True)

    records: list[dict[str, str]] = []
    for row in dataset:
        celex_id = str(row.get("celex_id") or row.get("id") or len(records))
        titles = row.get("titles", {}) or {}
        texts = row.get("texts", {}) or {}
        for lang in args.languages:
            text = texts.get(lang) or texts.get(lang.upper())
            if not text:
                continue
            title = titles.get(lang) or titles.get(lang.upper()) or f"CELEX {celex_id}"
            records.append(
                {
                    "document_id": f"{celex_id}_{lang}",
                    "celex_id": celex_id,
                    "language": lang,
                    "title": str(title),
                    "text": str(text),
                }
            )
        if len(records) >= args.sample:
            break

    output_path = OUTPUT_DIR / f"sample_{args.sample}.jsonl"
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Wrote {len(records)} records to {output_path}")


if __name__ == "__main__":
    main()
