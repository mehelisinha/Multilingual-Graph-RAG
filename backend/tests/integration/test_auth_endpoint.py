"""Integration tests for authentication endpoints."""

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.db.models.user import User


@pytest.mark.integration
async def test_login_success(client: AsyncClient, seeded_user: User) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": seeded_user.email, "password": "Password123!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"
    assert body["expires_in"] > 0


@pytest.mark.integration
async def test_login_invalid_credentials(client: AsyncClient, seeded_user: User) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": seeded_user.email, "password": "WrongPassword!"},
    )
    assert response.status_code == 401


@pytest.mark.integration
async def test_refresh_token_flow(
    client: AsyncClient,
    seeded_user: User,
    mock_redis: AsyncMock,
) -> None:
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": seeded_user.email, "password": "Password123!"},
    )
    refresh_token = login_response.json()["refresh_token"]
    mock_redis.get = AsyncMock(return_value=str(seeded_user.id))

    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()


@pytest.mark.integration
async def test_me_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.integration
async def test_me_returns_profile(client: AsyncClient, seeded_user: User) -> None:
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": seeded_user.email, "password": "Password123!"},
    )
    access_token = login_response.json()["access_token"]

    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert me_response.status_code == 200
    body = me_response.json()
    assert body["email"] == seeded_user.email
    assert body["id"] == str(seeded_user.id)
