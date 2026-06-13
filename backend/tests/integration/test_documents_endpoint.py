"""Documents endpoint integration tests."""

import uuid

import pytest
from httpx import AsyncClient

_MISSING_DOC_ID = str(uuid.uuid4())


@pytest.mark.asyncio
async def test_list_documents_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/documents")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_documents_for_regular_user(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    response = await client.get("/api/v1/documents", headers=user_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_delete_document_forbidden_for_non_admin(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    response = await client.delete(f"/api/v1/documents/{_MISSING_DOC_ID}", headers=user_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_missing_document_returns_404(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    response = await client.delete(f"/api/v1/documents/{_MISSING_DOC_ID}", headers=admin_headers)
    assert response.status_code == 404
