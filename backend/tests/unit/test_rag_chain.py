"""RAG chain orchestration tests."""

import pytest

from app.api.v1.schemas.query import ChunkResult, QueryRequest
from app.pipeline.generator import AnswerGenerator
from app.pipeline.rag_chain import RAGChain
from app.pipeline.retriever import Retriever


class _StubRetriever(Retriever):
    def retrieve(self, query: str, *, top_k: int | None = None, language: str | None = None):
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


class _StubGenerator(AnswerGenerator):
    async def stream_answer(self, query, chunks, answer_language):
        yield "Test "
        yield "answer."


@pytest.mark.asyncio
async def test_rag_chain_streams_metadata_chunks_and_tokens(test_settings) -> None:
    chain = RAGChain(
        retriever=_StubRetriever(settings=test_settings),
        generator=_StubGenerator(test_settings),
        settings=test_settings,
    )
    events = [event async for event in chain.stream(QueryRequest(query="GDPR Article 17"))]

    types = [event.type for event in events]
    assert types[0] == "metadata"
    assert "chunks" in types
    assert "token" in types
    assert types[-1] == "done"
    assert events[-1].answer == "Test answer."
