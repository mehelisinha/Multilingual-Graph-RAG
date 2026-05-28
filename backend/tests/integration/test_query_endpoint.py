"""Query endpoint integration tests."""

from collections.abc import AsyncIterator

import pytest

from app.api.v1.schemas.query import ChunkResult, QueryRequest, QueryStreamEvent
from app.dependencies import get_rag_chain
from app.pipeline.rag_chain import RAGChain


class _StubRAGChain(RAGChain):
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


@pytest.mark.asyncio
async def test_query_endpoint_requires_auth(client) -> None:
    response = await client.post("/api/v1/query", json={"query": "GDPR"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_query_endpoint_streams_sse(client, app, seeded_user) -> None:
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "Password123!"},
    )
    token = login.json()["access_token"]

    app.dependency_overrides[get_rag_chain] = lambda: _StubRAGChain()
    response = await client.post(
        "/api/v1/query",
        json={"query": "What is GDPR Article 17?", "language": "auto", "top_k": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")
    body = response.text
    assert "metadata" in body
    assert "chunks" in body
    assert "Hello" in body
