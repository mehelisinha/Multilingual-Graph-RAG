"""IngestionJob ORM model."""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class IngestionJob(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ingestion_jobs"

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)
    current_stage: Mapped[str] = mapped_column(String(50), nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False) # 0-100
    error_message: Mapped[str] = mapped_column(String, nullable=True)
