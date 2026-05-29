"""Query endpoint integration tests."""

import pytest
from httpx import AsyncClient

from app.dependencies import get_rag_chain
from tests.doubles import StubRAGChain


@pytest.mark.asyncio
async def test_query_endpoint_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/api/v1/query", json={"query": "GDPR"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_query_endpoint_streams_sse(client: AsyncClient, app, seeded_user) -> None:
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "Password123!"},
    )
    token = login.json()["access_token"]

    app.dependency_overrides[get_rag_chain] = lambda: StubRAGChain()
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
