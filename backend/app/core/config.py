"""Application settings loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration — all values sourced from env / .env files."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local", "../.env", "../.env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    environment: Literal["development", "production", "test"] = "development"
    secret_key: str = Field(
        default="dev-secret-key-minimum-32-characters-long",
        min_length=32,
    )
    access_token_expire_minutes: int = Field(default=1440, ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)
    allowed_origins: str = "http://localhost:5173"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "rag_platform"
    postgres_user: str = "raguser"
    postgres_password: str = "changeme"

    milvus_host: str = "localhost"
    milvus_port: int = 19530
    milvus_collection_name: str = "multilingual_chunks"

    embedding_model: str = "intfloat/multilingual-e5-large"
    embedding_dimension: int = Field(default=1024, ge=1)
    fasttext_model_path: str = "./models/lid.176.bin"

    llm_provider: Literal["ollama", "openai", "groq"] = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral:7b-instruct"
    openai_api_key: str = ""
    groq_api_key: str = ""

    default_top_k: int = Field(default=10, ge=1, le=20)

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "changeme"
    neo4j_database: str = "neo4j"

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    bootstrap_admin_email: str | None = None
    bootstrap_admin_password: str | None = None
    database_url_override: str | None = Field(default=None, alias="DATABASE_URL")

    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "multilingual-graph-rag"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self.database_url_override
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def milvus_uri(self) -> str:
        return f"http://{self.milvus_host}:{self.milvus_port}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
