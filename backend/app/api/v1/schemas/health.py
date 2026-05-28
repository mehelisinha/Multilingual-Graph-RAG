"""Health check response schemas."""

from typing import Literal

from pydantic import BaseModel

ServiceStatus = Literal["up", "down"]
OverallStatus = Literal["healthy", "degraded", "unhealthy"]


class HealthResponse(BaseModel):
    status: OverallStatus
    postgres: ServiceStatus
    redis: ServiceStatus
    neo4j: ServiceStatus
    milvus: ServiceStatus
