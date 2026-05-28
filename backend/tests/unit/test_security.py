"""Unit tests for password hashing and JWT utilities."""

from uuid import uuid4

import jwt
import pytest

from app.core.config import Settings
from app.core.security import (
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

TEST_SETTINGS = Settings(
    environment="test",
    secret_key="test-secret-key-minimum-32-characters-long",
    access_token_expire_minutes=30,
    refresh_token_expire_days=1,
)


@pytest.mark.unit
def test_hash_and_verify_password() -> None:
    hashed = hash_password("SecurePass123!")
    assert hashed != "SecurePass123!"
    assert verify_password("SecurePass123!", hashed)
    assert not verify_password("WrongPassword!", hashed)


@pytest.mark.unit
def test_access_token_roundtrip() -> None:
    user_id = uuid4()
    token = create_access_token(user_id, settings=TEST_SETTINGS)
    payload = decode_token(token, settings=TEST_SETTINGS)
    assert payload["sub"] == str(user_id)
    assert payload["type"] == TOKEN_TYPE_ACCESS


@pytest.mark.unit
def test_refresh_token_type() -> None:
    user_id = uuid4()
    token = create_refresh_token(user_id, settings=TEST_SETTINGS)
    payload = decode_token(token, settings=TEST_SETTINGS)
    assert payload["type"] == TOKEN_TYPE_REFRESH


@pytest.mark.unit
def test_invalid_token_raises() -> None:
    with pytest.raises(jwt.PyJWTError):
        decode_token("not-a-valid-token", settings=TEST_SETTINGS)
