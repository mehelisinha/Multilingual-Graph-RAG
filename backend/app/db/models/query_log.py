"""QueryLog ORM model."""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class QueryLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "query_logs"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    query_text: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=True)
    top_k: Mapped[int] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    results_count: Mapped[int] = mapped_column(Integer, nullable=True)
