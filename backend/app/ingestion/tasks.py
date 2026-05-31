"""Celery task definitions for asynchronous ingestion and graph building."""

import asyncio
from typing import Any

import structlog

from app.core.config import get_settings
from app.graph.graph_builder import build_document_graph
from app.graph.neo4j_client import neo4j_client
from app.ingestion.chunker import chunk_text
from app.ingestion.indexing import index_document_text
from app.ingestion.ner_extractor import ner_extractor
from app.workers.celery_app import celery_app

logger = structlog.get_logger(__name__)


def run_async(coro: Any) -> Any:
    """Helper to run a coroutine synchronously using the asyncio event loop."""
    try:
        return asyncio.run(coro)
    except RuntimeError:
        # Fallback if there is an existing event loop running in the thread
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def build_graph_for_document_task(
    self: Any,
    document_id: str,
    title: str,
    text: str,
    language: str | None = None,
) -> dict[str, Any]:
    """Asynchronously process a document: chunk, embed, index to Milvus, extract NER, and populate Neo4j."""
    logger.info("Starting document ingestion task", document_id=document_id, title=title)
    try:
        settings = get_settings()

        # 1. Index document chunks and embeddings into Milvus (sync)
        total_chunks = index_document_text(
            document_id=document_id,
            title=title,
            text=text,
            language=language,
            settings=settings,
        )

        # 2. Re-chunk locally to identical chunks to extract NER entities
        resolved_language = language or "en"
        chunks = chunk_text(text, document_id=document_id, title=title, language=resolved_language)

        graph_chunks = []
        for chunk in chunks:
            entities = ner_extractor.extract_entities(chunk.text, language=resolved_language)
            graph_chunks.append(
                {
                    "id": chunk.id,
                    "text": chunk.text,
                    "embedding_id": chunk.id,
                    "chunk_index": chunk.chunk_index,
                    "token_count": chunk.token_count,
                    "language": chunk.language,
                    "entities": entities,
                }
            )

        doc = {
            "id": document_id,
            "title": title,
            "language": resolved_language,
            "source_url": "",
            "celex_id": "",
        }

        # 3. Populate Neo4j knowledge graph using the async build function
        async def run_neo4j_ingestion() -> None:
            await neo4j_client.connect()
            try:
                await build_document_graph(doc, graph_chunks)
            finally:
                await neo4j_client.close()

        run_async(run_neo4j_ingestion())

        logger.info(
            "Document ingestion task completed successfully",
            document_id=document_id,
            chunks_count=total_chunks,
        )
        return {
            "status": "success",
            "document_id": document_id,
            "chunks_count": total_chunks,
        }
    except Exception as exc:
        logger.exception("Document ingestion task failed", document_id=document_id, error=str(exc))
        try:
            self.retry(exc=exc)
        except Exception:
            return {
                "status": "failure",
                "document_id": document_id,
                "error": str(exc),
            }
