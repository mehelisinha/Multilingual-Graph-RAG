"""Redis async client and refresh-token storage."""

from collections.abc import AsyncGenerator
from typing import Final

import redis.asyncio as aioredis

from app.core.config import Settings, get_settings

REFRESH_TOKEN_PREFIX: Final[str] = "refresh_token:"

_redis_client: aioredis.Redis | None = None


def create_redis_client(settings: Settings | None = None) -> aioredis.Redis:
    cfg = settings or get_settings()
    client: aioredis.Redis = aioredis.from_url(  # type: ignore[no-untyped-call]
        cfg.redis_url,
        decode_responses=True,
    )
    return client


def get_redis_client() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = create_redis_client()
    return _redis_client


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    yield get_redis_client()


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


def configure_redis(settings: Settings) -> None:
    global _redis_client
    _redis_client = create_redis_client(settings)


def refresh_token_key(token: str) -> str:
    return f"{REFRESH_TOKEN_PREFIX}{token}"


async def store_refresh_token(
    token: str,
    user_id: str,
    *,
    ttl_seconds: int,
    client: aioredis.Redis | None = None,
) -> None:
    redis = client or get_redis_client()
    await redis.set(refresh_token_key(token), user_id, ex=ttl_seconds)


async def get_refresh_token_user_id(
    token: str,
    *,
    client: aioredis.Redis | None = None,
) -> str | None:
    redis = client or get_redis_client()
    value = await redis.get(refresh_token_key(token))
    return str(value) if value is not None else None


async def revoke_refresh_token(
    token: str,
    *,
    client: aioredis.Redis | None = None,
) -> None:
    redis = client or get_redis_client()
    await redis.delete(refresh_token_key(token))


async def ping_redis(client: aioredis.Redis | None = None) -> bool:
    redis = client or get_redis_client()
    try:
        return bool(await redis.ping())
    except Exception:
        return False
