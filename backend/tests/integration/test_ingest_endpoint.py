"""Ingest endpoint integration tests."""

from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient

_HTML_UPLOAD = {"file": ("sample.html", b"<html><body>Hello</body></html>", "text/html")}


@pytest.mark.asyncio
async def test_ingest_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/api/v1/ingest", files=_HTML_UPLOAD)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_ingest_forbidden_for_non_admin(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    response = await client.post("/api/v1/ingest", files=_HTML_UPLOAD, headers=user_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_ingest_rejects_unsupported_extension(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    response = await client.post(
        "/api/v1/ingest",
        files={"file": ("malware.exe", b"MZ", "application/octet-stream")},
        headers=admin_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_ingest_creates_job_for_admin(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    with patch("app.ingestion.tasks.run_ingestion_pipeline_task") as mock_task:
        mock_task.delay = MagicMock()
        response = await client.post("/api/v1/ingest", files=_HTML_UPLOAD, headers=admin_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PENDING"
    assert body["job_id"]
    assert body["document_id"]
    mock_task.delay.assert_called_once()
