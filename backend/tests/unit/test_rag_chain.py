"""RAG chain orchestration tests."""

import pytest

from app.api.v1.schemas.query import QueryRequest
from app.core.config import Settings
from app.pipeline.rag_chain import RAGChain
from tests.doubles import StubAnswerGenerator, StubRetriever


@pytest.mark.asyncio
async def test_rag_chain_streams_metadata_chunks_and_tokens(test_settings: Settings) -> None:
    chain = RAGChain(
        retriever=StubRetriever(),
        generator=StubAnswerGenerator(),
        settings=test_settings,
    )
    events = [event async for event in chain.stream(QueryRequest(query="GDPR Article 17"))]

    types = [event.type for event in events]
    assert types[0] == "metadata"
    assert "chunks" in types
    assert "token" in types
    assert types[-1] == "done"
    assert events[-1].answer == "Test answer."
