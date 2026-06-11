"""Shared document indexing: chunk → embed → Milvus (used by API jobs and data scripts)."""

from app.core.config import Settings, get_settings
from app.db.milvus import MilvusStore
from app.ingestion.chunker import chunk_text
from app.pipeline.embedder import Embedder
from app.pipeline.lang_detect import detect_language
from app.pipeline.types import TextChunk


def index_document_text(
    *,
    document_id: str,
    title: str,
    text: str,
    language: str | None = None,
    settings: Settings | None = None,
) -> list[TextChunk]:
    """Chunk, embed, and upsert a single document into Milvus.

    Returns the chunks produced so callers can reuse them (e.g. for NER) instead
    of re-chunking the same text.
    """
    cfg = settings or get_settings()
    resolved_language = language or detect_language(text, cfg)
    chunks: list[TextChunk] = chunk_text(
        text,
        document_id=document_id,
        title=title,
        language=resolved_language,
    )
    if not chunks:
        return []

    embedder = Embedder(cfg)
    vectors = embedder.embed_passages([chunk.text for chunk in chunks])
    store = MilvusStore(cfg)
    store.insert_chunks(chunks, vectors)
    return chunks
