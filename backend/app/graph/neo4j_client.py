"""Neo4j driver singleton + connection pool."""

from typing import Any

import structlog
from neo4j import AsyncDriver, AsyncGraphDatabase

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class Neo4jClient:
    def __init__(self) -> None:
        self.driver: AsyncDriver | None = None

    async def connect(self) -> None:
        if not self.driver:
            self.driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
            await self.driver.verify_connectivity()
            logger.info("Connected to Neo4j", uri=settings.neo4j_uri)

    async def close(self) -> None:
        if self.driver:
            await self.driver.close()
            self.driver = None
            logger.info("Closed Neo4j connection")

    async def execute_query(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        if not self.driver:
            await self.connect()
        assert self.driver is not None

        async with self.driver.session(database=settings.neo4j_database) as session:
            result = await session.run(query, parameters, **kwargs)
            return await result.data()

neo4j_client = Neo4jClient()
