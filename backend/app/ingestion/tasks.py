"""Celery task definitions for asynchronous document ingestion and graph building."""

import asyncio
from typing import Any

import structlog
from sqlalchemy import update

from app.core.config import get_settings
from app.db.models.document import Document
from app.db.models.job import IngestionJob
from app.db.postgres import get_session_factory
from app.graph.graph_builder import build_document_graph
from app.graph.neo4j_client import neo4j_client
from app.ingestion.indexing import index_document_text
from app.ingestion.ner_extractor import ner_extractor
from app.ingestion.pipeline import process_file_to_text
from app.pipeline.types import TextChunk
from app.workers.celery_app import celery_app

logger = structlog.get_logger(__name__)


# A single long-lived loop per worker process. The async SQLAlchemy engine and
# Neo4j driver cache connections bound to the loop they were created on, so every
# coroutine must run on the same loop — asyncio.run() per call would create a new
# loop each time and fail with "Future attached to a different loop".
_worker_loop: asyncio.AbstractEventLoop | None = None


def run_async(coro: Any) -> Any:
    """Run a coroutine synchronously from within a Celery worker thread."""
    global _worker_loop
    if _worker_loop is None or _worker_loop.is_closed():
        _worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_worker_loop)
    return _worker_loop.run_until_complete(coro)


def _chunks_to_graph_payload(
    chunks: list[TextChunk],
    language: str,
) -> list[dict[str, Any]]:
    """Run NER on each chunk and shape it for the Neo4j graph builder."""
    payload: list[dict[str, Any]] = []
    for chunk in chunks:
        entities = ner_extractor.extract_entities(chunk.text, language=language)
        payload.append(
            {
                "id": chunk.chunk_id,
                "text": chunk.text,
                "embedding_id": chunk.chunk_id,
                "chunk_index": chunk.chunk_index,
                "token_count": len(chunk.text.split()),
                "language": chunk.language,
                "entities": entities,
            }
        )
    return payload


async def _update_job(
    job_id: str,
    stage: str,
    progress: int,
    status: str = "PROCESSING",
    error: str | None = None,
) -> None:
    async with get_session_factory()() as session:
        await session.execute(
            update(IngestionJob)
            .where(IngestionJob.id == job_id)
            .values(current_stage=stage, progress=progress, status=status, error_message=error)
        )
        await session.commit()


async def _set_document_status(
    document_id: str,
    status: str,
    chunk_count: int | None = None,
) -> None:
    values: dict[str, Any] = {"status": status}
    if chunk_count is not None:
        values["chunk_count"] = chunk_count
    async with get_session_factory()() as session:
        await session.execute(
            update(Document).where(Document.id == document_id).values(**values)
        )
        await session.commit()


async def _populate_graph(doc: dict[str, Any], graph_chunks: list[dict[str, Any]]) -> None:
    await neo4j_client.connect()
    try:
        await build_document_graph(doc, graph_chunks)
    finally:
        await neo4j_client.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)  # type: ignore[untyped-decorator]
def run_ingestion_pipeline_task(
    self: Any,
    document_id: str,
    job_id: str,
    file_path: str,
    title: str,
    language: str | None = None,
) -> dict[str, Any]:
    """Parse a file, index its chunks to Milvus, extract entities, and build the graph."""
    logger.info("ingestion_pipeline_started", document_id=document_id, job_id=job_id)
    try:
        run_async(_update_job(job_id, "PARSING", 10))
        text = process_file_to_text(file_path)

        run_async(_update_job(job_id, "CHUNKING_AND_EMBEDDING", 40))
        settings = get_settings()
        chunks = index_document_text(
            document_id=document_id,
            title=title,
            text=text,
            language=language,
            settings=settings,
        )

        run_async(_update_job(job_id, "EXTRACTING_ENTITIES", 70))
        resolved_language = language or (chunks[0].language if chunks else "en")
        graph_chunks = _chunks_to_graph_payload(chunks, resolved_language)

        run_async(_update_job(job_id, "BUILDING_GRAPH", 90))
        doc = {
            "id": document_id,
            "title": title,
            "language": resolved_language,
            "source_url": "",
            "celex_id": "",
        }
        run_async(_populate_graph(doc, graph_chunks))

        run_async(_update_job(job_id, "COMPLETED", 100, status="COMPLETED"))
        run_async(_set_document_status(document_id, "COMPLETED", chunk_count=len(chunks)))

        logger.info("ingestion_pipeline_completed", document_id=document_id, chunks=len(chunks))
        return {"status": "success", "document_id": document_id, "chunks_count": len(chunks)}
    except Exception as exc:
        logger.exception("ingestion_pipeline_failed", document_id=document_id, error=str(exc))
        run_async(_update_job(job_id, "FAILED", 0, status="FAILED", error=str(exc)))
        run_async(_set_document_status(document_id, "FAILED"))
        try:
            self.retry(exc=exc)
            return {"status": "retrying"}
        except Exception:
            return {"status": "failure", "document_id": document_id, "error": str(exc)}
