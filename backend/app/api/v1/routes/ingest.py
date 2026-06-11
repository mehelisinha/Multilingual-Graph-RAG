"""POST /ingest — upload and start job."""

import asyncio
import os
import uuid
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models.document import Document
from app.db.models.job import IngestionJob
from app.db.models.user import User
from app.dependencies import get_current_user, get_db
from app.ingestion.pipeline import SUPPORTED_EXTENSIONS

router = APIRouter(prefix="/ingest", tags=["ingest"])

_UPLOAD_CHUNK_BYTES = 1024 * 1024  # stream in 1 MiB blocks


@router.post("")
async def ingest_document(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    language: str | None = Form(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Upload a document to trigger the async ingestion pipeline."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Supported: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    doc_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())

    # Create Document record
    doc = Document(
        id=doc_id,
        filename=file.filename,
        title=title or file.filename,
        language=language,
        size_bytes=file.size or 0,
        status="PENDING",
    )
    session.add(doc)

    # Create Job record
    job = IngestionJob(
        id=job_id,
        document_id=doc_id,
        status="PENDING",
        current_stage="UPLOADED",
        progress=0,
    )
    session.add(job)
    await session.commit()

    # Stream the upload to disk in blocks to avoid loading large files into memory.
    upload_dir = get_settings().upload_dir
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{doc_id}_{file.filename}")
    with open(file_path, "wb") as f:
        while block := await file.read(_UPLOAD_CHUNK_BYTES):
            f.write(block)

    # Dispatch the async ingestion pipeline.
    from app.ingestion.tasks import run_ingestion_pipeline_task

    run_ingestion_pipeline_task.delay(doc_id, job_id, file_path, title or file.filename, language)

    return {"job_id": job_id, "document_id": doc_id, "status": "PENDING"}


@router.websocket("/ws/{job_id}")
async def websocket_job_status(websocket: WebSocket, job_id: str) -> None:
    """Stream job status updates via WebSocket."""
    await websocket.accept()
    from app.db.postgres import get_session_factory

    session_factory = get_session_factory()
    try:
        while True:
            async with session_factory() as session:
                result = await session.execute(select(IngestionJob).where(IngestionJob.id == job_id))
                job = result.scalar_one_or_none()
                if job:
                    await websocket.send_json({
                        "job_id": job.id,
                        "status": job.status,
                        "current_stage": job.current_stage,
                        "progress": job.progress,
                        "error_message": job.error_message,
                    })
                    if job.status in ["COMPLETED", "FAILED"]:
                        break
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
