"""Authentication business logic."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationError
from app.core.security import (
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.models.user import User
from app.db.redis import (
    get_refresh_token_user_id,
    revoke_refresh_token,
    store_refresh_token,
)
from app.services.user_service import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession, settings: Settings | None = None) -> None:
        self._users = UserRepository(session)
        self._settings = settings or get_settings()

    async def authenticate(self, email: str, password: str) -> User:
        user = await self._users.get_by_email(email.lower())
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        if not user.is_active:
            raise AuthenticationError("Account is inactive")
        return user

    async def issue_tokens(self, user: User) -> tuple[str, str, int]:
        access_token = create_access_token(user.id, settings=self._settings)
        refresh_token = create_refresh_token(user.id, settings=self._settings)
        ttl_seconds = self._settings.refresh_token_expire_days * 24 * 60 * 60
        await store_refresh_token(refresh_token, str(user.id), ttl_seconds=ttl_seconds)
        return access_token, refresh_token, self._settings.access_token_expire_minutes * 60

    async def refresh_access_token(self, refresh_token: str) -> tuple[str, int]:
        payload = self._decode_refresh_token(refresh_token)
        stored_user_id = await get_refresh_token_user_id(refresh_token)
        if stored_user_id is None or stored_user_id != payload["sub"]:
            raise AuthenticationError("Refresh token revoked or expired")

        user = await self._users.get_by_id(UUID(payload["sub"]))
        if user is None or not user.is_active:
            raise AuthenticationError("User no longer active")

        access_token = create_access_token(user.id, settings=self._settings)
        return access_token, self._settings.access_token_expire_minutes * 60

    async def logout(self, refresh_token: str) -> None:
        await revoke_refresh_token(refresh_token)

    async def bootstrap_admin_if_needed(self) -> None:
        email = self._settings.bootstrap_admin_email
        password = self._settings.bootstrap_admin_password
        if not email or not password:
            return
        if await self._users.count() > 0:
            return
        await self._users.create(
            email=email.lower(),
            hashed_password=hash_password(password),
            is_admin=True,
        )

    @staticmethod
    def _decode_refresh_token(refresh_token: str) -> dict[str, str]:
        try:
            payload = decode_token(refresh_token)
        except Exception as exc:
            raise AuthenticationError("Invalid refresh token") from exc
        if payload.get("type") != TOKEN_TYPE_REFRESH:
            raise AuthenticationError("Invalid token type")
        return payload

    @staticmethod
    def decode_access_token(access_token: str) -> UUID:
        try:
            payload = decode_token(access_token)
        except Exception as exc:
            raise AuthenticationError() from exc
        if payload.get("type") != TOKEN_TYPE_ACCESS:
            raise AuthenticationError("Invalid token type")
        return UUID(payload["sub"])
