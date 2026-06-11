"""POST /query — multilingual RAG endpoint with SSE streaming, plus query history."""

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.query import QueryRequest
from app.db.models.query_log import QueryLog
from app.db.models.user import User
from app.dependencies import get_current_user, get_db, get_rag_chain
from app.pipeline.rag_chain import RAGChain
from app.pipeline.streaming import sse_event_stream

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_class=StreamingResponse)
async def query_documents(
    body: QueryRequest,
    user: User = Depends(get_current_user),
    chain: RAGChain = Depends(get_rag_chain),
    session: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    # Record the query for per-user history (FR-5.3). Logging failures must not
    # block the answer, so the insert is best-effort.
    session.add(
        QueryLog(
            user_id=user.id,
            query_text=body.query,
            language=None if body.language == "auto" else body.language,
            top_k=body.top_k,
        )
    )
    await session.commit()

    return StreamingResponse(
        sse_event_stream(chain.stream(body)),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history")
async def query_history(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Return the authenticated user's 50 most recent queries."""
    result = await session.execute(
        select(QueryLog)
        .where(QueryLog.user_id == user.id)
        .order_by(QueryLog.created_at.desc())
        .limit(50)
    )
    return [
        {
            "id": log.id,
            "query_text": log.query_text,
            "language": log.language,
            "top_k": log.top_k,
            "created_at": log.created_at,
        }
        for log in result.scalars().all()
    ]
