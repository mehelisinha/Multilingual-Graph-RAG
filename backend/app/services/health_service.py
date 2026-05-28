"""Health check service for infrastructure dependencies."""

from typing import Literal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.redis import ping_redis

ServiceStatus = Literal["up", "down"]


class HealthService:
    def __init__(self, session: AsyncSession, settings: Settings | None = None) -> None:
        self._session = session
        self._settings = settings or get_settings()

    async def check_postgres(self) -> ServiceStatus:
        try:
            await self._session.execute(text("SELECT 1"))
            return "up"
        except Exception:
            return "down"

    async def check_redis(self) -> ServiceStatus:
        return "up" if await ping_redis() else "down"

    async def check_neo4j(self) -> ServiceStatus:
        try:
            from neo4j import AsyncGraphDatabase

            driver = AsyncGraphDatabase.driver(
                self._settings.neo4j_uri,
                auth=(self._settings.neo4j_user, self._settings.neo4j_password),
            )
            async with driver.session(database=self._settings.neo4j_database) as session:
                await session.run("RETURN 1")
            await driver.close()
            return "up"
        except Exception:
            return "down"

    async def check_milvus(self) -> ServiceStatus:
        try:
            from pymilvus import connections, utility

            alias = "health_check"
            connections.connect(
                alias=alias,
                host=self._settings.milvus_host,
                port=str(self._settings.milvus_port),
            )
            healthy = utility.get_server_version() is not None
            connections.disconnect(alias)
            return "up" if healthy else "down"
        except Exception:
            return "down"

    async def get_health(self) -> dict[str, str]:
        postgres = await self.check_postgres()
        redis = await self.check_redis()
        neo4j = await self.check_neo4j()
        milvus = await self.check_milvus()

        statuses = [postgres, redis, neo4j, milvus]
        if all(status == "up" for status in statuses):
            overall = "healthy"
        elif postgres == "up" and redis == "up":
            overall = "degraded"
        else:
            overall = "unhealthy"

        return {
            "status": overall,
            "postgres": postgres,
            "redis": redis,
            "neo4j": neo4j,
            "milvus": milvus,
        }
