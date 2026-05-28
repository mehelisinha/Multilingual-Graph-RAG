"""JWT encoding/decoding and password hashing utilities."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import bcrypt
import jwt

from app.core.config import Settings, get_settings

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def _build_expiry(minutes: int | None = None, days: int | None = None) -> datetime:
    now = datetime.now(tz=UTC)
    if days is not None:
        return now + timedelta(days=days)
    return now + timedelta(minutes=minutes or 0)


def create_access_token(
    subject: UUID,
    *,
    settings: Settings | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    cfg = settings or get_settings()
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": TOKEN_TYPE_ACCESS,
        "iss": cfg.jwt_issuer,
        "exp": _build_expiry(minutes=cfg.access_token_expire_minutes),
        "iat": datetime.now(tz=UTC),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, cfg.secret_key, algorithm=cfg.jwt_algorithm)


def create_refresh_token(
    subject: UUID,
    *,
    settings: Settings | None = None,
) -> str:
    cfg = settings or get_settings()
    payload = {
        "sub": str(subject),
        "type": TOKEN_TYPE_REFRESH,
        "iss": cfg.jwt_issuer,
        "exp": _build_expiry(days=cfg.refresh_token_expire_days),
        "iat": datetime.now(tz=UTC),
    }
    return jwt.encode(payload, cfg.secret_key, algorithm=cfg.jwt_algorithm)


def decode_token(token: str, *, settings: Settings | None = None) -> dict[str, Any]:
    cfg = settings or get_settings()
    return jwt.decode(
        token,
        cfg.secret_key,
        algorithms=[cfg.jwt_algorithm],
        issuer=cfg.jwt_issuer,
        options={"require": ["exp", "sub", "type", "iss"]},
    )
