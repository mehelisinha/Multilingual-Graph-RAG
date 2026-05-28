"""FastAPI application factory and lifespan hooks."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging, get_logger
from app.core.middleware import register_middleware
from app.db.postgres import dispose_engine, get_session_factory
from app.db.redis import close_redis
from app.services.auth_service import AuthService

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    configure_logging(environment=settings.environment)
    logger.info("application_starting", environment=settings.environment)

    session_factory = get_session_factory()
    async with session_factory() as session:
        auth_service = AuthService(session, settings=settings)
        await auth_service.bootstrap_admin_if_needed()
        await session.commit()

    yield

    await close_redis()
    await dispose_engine()
    logger.info("application_shutdown")


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or get_settings()
    app = FastAPI(
        title="Multilingual Graph RAG Platform",
        version="0.1.0",
        docs_url="/docs" if cfg.is_development else None,
        redoc_url="/redoc" if cfg.is_development else None,
        lifespan=lifespan,
    )
    app.state.settings = cfg
    register_middleware(app, cfg)
    app.include_router(api_router, prefix="/api/v1")
    Instrumentator().instrument(app)
    return app


app = create_app()
