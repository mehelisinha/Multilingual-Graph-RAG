#!/usr/bin/env python3
"""Batch NER and Neo4j graph population from downloaded MultiEURLEX JSONL records."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from typing import Any

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.graph.graph_builder import build_document_graph  # noqa: E402
from app.graph.neo4j_client import neo4j_client  # noqa: E402
from app.ingestion.chunker import chunk_text  # noqa: E402
from app.ingestion.ner_extractor import ner_extractor  # noqa: E402

DEFAULT_INPUT = ROOT / "data" / "raw" / "multieurlex"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Populate Neo4j knowledge graph from JSONL documents"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Path to JSONL file or directory (default: latest sample in data/raw/multieurlex)",
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Max documents to ingest"
    )
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


async def process_records(records: list[dict[str, Any]]) -> None:
    try:
        # Verify Neo4j connectivity before running
        await neo4j_client.connect()

        for record in tqdm(records, desc="Building Graph"):
            doc_id = str(record["document_id"])
            celex_id = str(record.get("celex_id", ""))
            language = str(record.get("language", "en"))
            title = str(record.get("title", doc_id))
            text = str(record["text"])

            # 1. Build document dict
            doc = {
                "id": doc_id,
                "title": title,
                "language": language,
                "source_url": f"https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:{celex_id}"
                if celex_id
                else "",
                "celex_id": celex_id,
            }

            # 2. Chunk text semantically
            chunks = chunk_text(
                text, document_id=doc_id, title=title, language=language
            )

            # 3. Extract entities for each chunk and prepare graph chunks
            graph_chunks = []
            for chunk in chunks:
                entities = ner_extractor.extract_entities(chunk.text, language=language)
                graph_chunks.append(
                    {
                        "id": chunk.id,
                        "text": chunk.text,
                        "embedding_id": chunk.id,  # Map directly
                        "chunk_index": chunk.chunk_index,
                        "token_count": chunk.token_count,
                        "language": chunk.language,
                        "entities": entities,
                    }
                )

            # 4. Populate Neo4j
            await build_document_graph(doc, graph_chunks)

    finally:
        await neo4j_client.close()


async def async_main() -> None:
    args = parse_args()
    input_path = resolve_input(args.input)

    records = list(iter_records(input_path))
    if args.limit:
        records = records[: args.limit]

    print(
        f"Starting batch graph building for {len(records)} documents from {input_path}"
    )
    await process_records(records)
    print("Graph building completed successfully!")


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
