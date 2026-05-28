"""Shared FastAPI dependency injection."""

from collections.abc import AsyncGenerator
from functools import lru_cache

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.db.models.user import User
from app.db.postgres import get_db_session
from app.pipeline.rag_chain import RAGChain
from app.services.auth_service import AuthService
from app.services.user_service import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache
def get_rag_chain() -> RAGChain:
    return RAGChain()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


async def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(session)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationError()

    auth_service = AuthService(session)
    user_id = auth_service.decode_access_token(credentials.credentials)
    user = await UserRepository(session).get_by_id(user_id)
    if user is None or not user.is_active:
        raise AuthenticationError()
    return user
