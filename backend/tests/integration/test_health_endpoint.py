"""Integration tests for health endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
async def test_health_endpoint(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"healthy", "degraded", "unhealthy"}
    assert body["postgres"] in {"up", "down"}
    assert body["redis"] in {"up", "down"}
    assert body["neo4j"] in {"up", "down"}
    assert body["milvus"] in {"up", "down"}


@pytest.mark.integration
async def test_metrics_endpoint(client: AsyncClient) -> None:
    response = await client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
