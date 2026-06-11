"""GET /jobs — query job status."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.job import IngestionJob
from app.db.models.user import User
from app.dependencies import get_current_user, get_db

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.get("/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    result = await session.execute(select(IngestionJob).where(IngestionJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    return {
        "job_id": job.id,
        "document_id": job.document_id,
        "status": job.status,
        "current_stage": job.current_stage,
        "progress": job.progress,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }
