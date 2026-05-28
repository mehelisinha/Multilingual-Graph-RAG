"""Semantic chunking respecting sentence boundaries."""

import re

from app.pipeline.constants import MAX_CHUNK_CHARS, MIN_CHUNK_CHARS, TARGET_CHUNK_CHARS
from app.pipeline.types import TextChunk

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


def _estimate_chars(text: str) -> int:
    return len(text)


def chunk_text(
    text: str,
    *,
    document_id: str,
    title: str,
    language: str,
) -> list[TextChunk]:
    """Split document text into sentence-aware chunks."""
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []

    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(normalized) if s.strip()]
    if not sentences:
        sentences = [normalized]

    chunks: list[TextChunk] = []
    buffer: list[str] = []
    buffer_len = 0
    chunk_index = 0

    def flush() -> None:
        nonlocal chunk_index, buffer, buffer_len
        if not buffer:
            return
        chunk_text_value = " ".join(buffer).strip()
        if _estimate_chars(chunk_text_value) >= MIN_CHUNK_CHARS or not chunks:
            chunks.append(
                TextChunk(
                    document_id=document_id,
                    chunk_index=chunk_index,
                    text=chunk_text_value,
                    language=language,
                    title=title,
                )
            )
            chunk_index += 1
        buffer = []
        buffer_len = 0

    for sentence in sentences:
        sentence_len = _estimate_chars(sentence)
        if sentence_len > MAX_CHUNK_CHARS:
            flush()
            chunks.append(
                TextChunk(
                    document_id=document_id,
                    chunk_index=chunk_index,
                    text=sentence[:MAX_CHUNK_CHARS],
                    language=language,
                    title=title,
                )
            )
            chunk_index += 1
            continue

        if buffer and buffer_len + sentence_len > TARGET_CHUNK_CHARS:
            flush()

        buffer.append(sentence)
        buffer_len += sentence_len

        if buffer_len >= TARGET_CHUNK_CHARS:
            flush()

    flush()
    return chunks
