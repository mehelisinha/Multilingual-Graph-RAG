"""Pydantic schemas for the query / RAG endpoint."""

from typing import Literal

from pydantic import BaseModel, Field

from app.pipeline.constants import DEFAULT_TOP_K, MAX_TOP_K, MIN_TOP_K, LanguageCode

StreamEventType = Literal["metadata", "chunks", "token", "done", "error"]


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    language: LanguageCode | Literal["auto"] | None = "auto"
    top_k: int = Field(default=DEFAULT_TOP_K, ge=MIN_TOP_K, le=MAX_TOP_K)
    use_graph: bool = False  # Phase 3


class ChunkResult(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    text: str
    language: str
    title: str
    score: float = Field(ge=0.0, le=1.0)


class QueryStreamEvent(BaseModel):
    type: StreamEventType
    detected_language: LanguageCode | None = None
    chunks: list[ChunkResult] | None = None
    token: str | None = None
    answer: str | None = None
    error: str | None = None
