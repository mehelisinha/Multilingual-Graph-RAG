#!/usr/bin/env python3
"""Batch embed MultiEURLEX JSONL records and load them into Milvus."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.config import get_settings  # noqa: E402
from app.ingestion.indexing import index_document_text  # noqa: E402

DEFAULT_INPUT = ROOT / "data" / "raw" / "multieurlex"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest JSONL documents into Milvus")
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Path to JSONL file or directory (default: latest sample in data/raw/multieurlex)",
    )
    parser.add_argument("--limit", type=int, default=None, help="Max records to ingest")
    return parser.parse_args()


def resolve_input(path: Path | None) -> Path:
    if path is not None:
        return path
    candidates = sorted(DEFAULT_INPUT.glob("sample_*.jsonl"), reverse=True)
    if not candidates:
        raise SystemExit(
            f"No JSONL found in {DEFAULT_INPUT}. Run download_multieurlex.py first."
        )
    return candidates[0]


def iter_records(path: Path):
    if path.is_dir():
        files = sorted(path.glob("*.jsonl"))
    else:
        files = [path]
    for file_path in files:
        with file_path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    yield json.loads(line)


def main() -> None:
    args = parse_args()
    input_path = resolve_input(args.input)
    settings = get_settings()
    total_chunks = 0
    count = 0

    records = list(iter_records(input_path))
    if args.limit:
        records = records[: args.limit]

    for record in tqdm(records, desc="Indexing"):
        inserted = index_document_text(
            document_id=str(record["document_id"]),
            title=str(record.get("title", record["document_id"])),
            text=str(record["text"]),
            language=str(record.get("language", "")) or None,
            settings=settings,
        )
        total_chunks += inserted
        count += 1

    print(f"Indexed {count} documents ({total_chunks} chunks) into {settings.milvus_collection_name}")


if __name__ == "__main__":
    main()
