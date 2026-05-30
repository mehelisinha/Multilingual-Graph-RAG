"""Test doubles for the RAG pipeline (no Milvus or LLM connections)."""

from collections.abc import AsyncIterator

from app.api.v1.schemas.query import ChunkResult, QueryRequest, QueryStreamEvent


class StubRetriever:
    """In-memory retriever stub; does not subclass Retriever to avoid Milvus init."""

    def retrieve(
        self,
        query: str,
        *,
        top_k: int | None = None,
        language: str | None = None,
    ) -> list[ChunkResult]:
        return [
            ChunkResult(
                id="doc:0",
                document_id="doc",
                chunk_index=0,
                text="Article 17 covers the right to erasure.",
                language="en",
                title="GDPR",
                score=0.92,
            )
        ]


class StubAnswerGenerator:
    async def stream_answer(
        self,
        query: str,
        chunks: list[ChunkResult],
        answer_language: str,
        graph_context: str = "",
    ) -> AsyncIterator[str]:
        yield "Test "
        yield "answer."


class StubRAGChain:
    """Minimal RAG chain double for API integration tests."""

    async def stream(self, request: QueryRequest) -> AsyncIterator[QueryStreamEvent]:
        yield QueryStreamEvent(type="metadata", detected_language="en")
        yield QueryStreamEvent(
            type="chunks",
            chunks=[
                ChunkResult(
                    id="1:0",
                    document_id="1",
                    chunk_index=0,
                    text="Sample chunk",
                    language="de",
                    title="Regulation",
                    score=0.8,
                )
            ],
        )
        yield QueryStreamEvent(type="token", token="Hello")
        yield QueryStreamEvent(type="done", answer="Hello")
