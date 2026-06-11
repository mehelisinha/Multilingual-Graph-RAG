"""GET /documents — CRUD for ingested documents."""

import asyncio
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.milvus import MilvusStore
from app.db.models.document import Document
from app.db.models.user import User
from app.dependencies import get_current_user, get_db
from app.graph.cypher_queries import DELETE_DOCUMENT
from app.graph.neo4j_client import neo4j_client

logger = get_logger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
async def list_documents(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    result = await session.execute(select(Document).order_by(Document.created_at.desc()))
    docs = result.scalars().all()

    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "title": doc.title,
            "language": doc.language,
            "size_bytes": doc.size_bytes,
            "chunk_count": doc.chunk_count,
            "status": doc.status,
            "created_at": doc.created_at,
        }
        for doc in docs
    ]


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    result = await session.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Best-effort removal from the vector store and knowledge graph. A failure in
    # either external store must not leave the relational row dangling, so we log
    # and continue rather than aborting the delete.
    try:
        await asyncio.to_thread(MilvusStore().delete_by_document, document_id)
    except Exception as exc:
        logger.warning("milvus_delete_failed", document_id=document_id, error=str(exc))

    try:
        await neo4j_client.execute_query(DELETE_DOCUMENT, {"doc_id": document_id})
    except Exception as exc:
        logger.warning("neo4j_delete_failed", document_id=document_id, error=str(exc))

    await session.delete(doc)
    await session.commit()

    return {"status": "success", "message": "Document deleted"}
