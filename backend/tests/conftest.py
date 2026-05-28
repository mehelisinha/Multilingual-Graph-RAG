"""Pytest fixtures for unit and integration tests."""

from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings, get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.models.user import User
from app.db.postgres import configure_engine, dispose_engine, get_engine
from app.dependencies import get_db
from app.main import create_app
from app.services.user_service import UserRepository

TEST_SECRET = "test-secret-key-minimum-32-characters-long"
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        environment="test",
        secret_key=TEST_SECRET,
        database_url_override=TEST_DATABASE_URL,
        redis_url="redis://localhost:6379/15",
        bootstrap_admin_email="admin@example.com",
        bootstrap_admin_password="AdminPass123!",
        allowed_origins="http://localhost:5173",
    )


@pytest_asyncio.fixture
async def test_engine(test_settings: Settings):
    configure_engine(test_settings)
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await dispose_engine()


@pytest_asyncio.fixture
async def session_factory(test_engine):
    return async_sessionmaker(test_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(session_factory) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def mock_redis() -> AsyncMock:
    mock = AsyncMock()
    mock.set = AsyncMock(return_value=True)
    mock.get = AsyncMock(return_value=None)
    mock.delete = AsyncMock(return_value=1)
    mock.ping = AsyncMock(return_value=True)
    return mock


@pytest_asyncio.fixture
async def seeded_user(db_session: AsyncSession) -> User:
    repo = UserRepository(db_session)
    user = await repo.create(
        email="user@example.com",
        hashed_password=hash_password("Password123!"),
        is_admin=False,
    )
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def client(
    test_settings: Settings,
    session_factory,
    mock_redis: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
    configure_engine(test_settings)
    app = create_app(test_settings)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session
            await session.commit()

    app.dependency_overrides[get_db] = override_get_db

    with (
        patch("app.db.redis.get_redis_client", return_value=mock_redis),
        patch("app.services.health_service.HealthService.check_neo4j", return_value="down"),
        patch("app.services.health_service.HealthService.check_milvus", return_value="down"),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clear_settings_cache() -> Generator[None, None, None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
