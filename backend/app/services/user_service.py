"""User repository — database access layer."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, *, email: str, hashed_password: str, is_admin: bool = False) -> User:
        user = User(email=email, hashed_password=hashed_password, is_admin=is_admin)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def count(self) -> int:
        result = await self._session.execute(select(User))
        return len(result.scalars().all())
