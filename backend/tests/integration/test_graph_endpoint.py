"""Graph endpoint integration tests."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

SUBGRAPH_RECORDS = [
    {
        "source": {"id": "ent_1", "name": "GDPR", "type": "LAW", "label": "Entity"},
        "target": {"id": "chunk_1", "name": "", "type": "", "label": "Chunk"},
        "rel_type": "MENTIONS",
    },
    # Duplicate relationship (reached via two paths) must be deduplicated
    {
        "source": {"id": "ent_1", "name": "GDPR", "type": "LAW", "label": "Entity"},
        "target": {"id": "chunk_1", "name": "", "type": "", "label": "Chunk"},
        "rel_type": "MENTIONS",
    },
    {
        "source": {"id": "doc_1", "name": "Regulation 2016/679", "type": "", "label": "Document"},
        "target": {"id": "chunk_1", "name": "", "type": "", "label": "Chunk"},
        "rel_type": "HAS_CHUNK",
    },
]


async def _auth_headers(client: AsyncClient) -> dict[str, str]:
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "Password123!"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.mark.asyncio
async def test_subgraph_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/graph/subgraph/ent_1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_subgraph_returns_nodes_and_links(client: AsyncClient, seeded_user) -> None:
    headers = await _auth_headers(client)

    with patch(
        "app.graph.neo4j_client.neo4j_client.execute_query",
        new_callable=AsyncMock,
        return_value=SUBGRAPH_RECORDS,
    ):
        response = await client.get("/api/v1/graph/subgraph/ent_1", headers=headers)

    assert response.status_code == 200
    data = response.json()

    node_ids = {node["id"] for node in data["nodes"]}
    assert node_ids == {"ent_1", "chunk_1", "doc_1"}
    for node in data["nodes"]:
        assert set(node) == {"id", "name", "type", "label"}

    assert data["links"] == [
        {"source": "ent_1", "target": "chunk_1", "type": "MENTIONS"},
        {"source": "doc_1", "target": "chunk_1", "type": "HAS_CHUNK"},
    ]


@pytest.mark.asyncio
async def test_subgraph_empty_result(client: AsyncClient, seeded_user) -> None:
    headers = await _auth_headers(client)

    with patch(
        "app.graph.neo4j_client.neo4j_client.execute_query",
        new_callable=AsyncMock,
        return_value=[],
    ):
        response = await client.get("/api/v1/graph/subgraph/missing", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"nodes": [], "links": []}
