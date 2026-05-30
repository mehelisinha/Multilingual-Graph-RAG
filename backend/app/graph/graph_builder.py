"""Build graph from NER output + doc metadata."""

from typing import Any

import structlog

from app.graph.cypher_queries import MERGE_CHUNK, MERGE_DOCUMENT, MERGE_ENTITY
from app.graph.neo4j_client import neo4j_client

logger = structlog.get_logger(__name__)


async def build_document_graph(
    doc: dict[str, Any], chunks: list[dict[str, Any]]
) -> None:
    """Populates Neo4j with Document, Chunks, and Entities."""
    try:
        # 1. Merge Document
        await neo4j_client.execute_query(
            MERGE_DOCUMENT,
            {
                "doc_id": doc["id"],
                "title": doc.get("title", ""),
                "language": doc.get("language", "en"),
                "source_url": doc.get("source_url", ""),
                "celex_id": doc.get("celex_id", ""),
            },
        )

        # 2. Merge Chunks & Entities
        for chunk in chunks:
            await neo4j_client.execute_query(
                MERGE_CHUNK,
                {
                    "doc_id": doc["id"],
                    "chunk_id": chunk["id"],
                    "text": chunk["text"],
                    "embedding_id": chunk.get("embedding_id", ""),
                    "chunk_index": chunk.get("chunk_index", 0),
                    "token_count": chunk.get("token_count", 0),
                    "language": chunk.get("language", "en"),
                },
            )

            # Entities
            for entity in chunk.get("entities", []):
                await neo4j_client.execute_query(
                    MERGE_ENTITY,
                    {
                        "chunk_id": chunk["id"],
                        "entity_id": f"{entity['name']}_{entity['type']}",
                        "entity_name": entity["name"],
                        "entity_type": entity["type"],
                        "language": doc.get("language", "en"),
                    },
                )

        logger.info("Graph built for document", doc_id=doc["id"], chunks_count=len(chunks))
    except Exception as e:
        logger.error("Failed to build graph", doc_id=doc["id"], error=str(e))
        raise
