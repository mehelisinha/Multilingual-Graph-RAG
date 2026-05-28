"""POST /query — multilingual RAG endpoint with SSE streaming."""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.v1.schemas.query import QueryRequest
from app.db.models.user import User
from app.dependencies import get_current_user, get_rag_chain
from app.pipeline.rag_chain import RAGChain
from app.pipeline.streaming import sse_event_stream

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_class=StreamingResponse)
async def query_documents(
    body: QueryRequest,
    _: User = Depends(get_current_user),
    chain: RAGChain = Depends(get_rag_chain),
) -> StreamingResponse:
    return StreamingResponse(
        sse_event_stream(chain.stream(body)),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
