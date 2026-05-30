"""Main RAG orchestration: detect → retrieve → generate (stream)."""

from collections.abc import AsyncIterator

from app.api.v1.schemas.query import QueryRequest, QueryStreamEvent
from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.pipeline.constants import LanguageCode
from app.pipeline.generator import AnswerGenerator
from app.pipeline.graph_enricher import get_graph_context
from app.pipeline.lang_detect import detect_language
from app.pipeline.retriever import Retriever

logger = get_logger(__name__)


class RAGChain:
    def __init__(
        self,
        retriever: Retriever | None = None,
        generator: AnswerGenerator | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._retriever = retriever or Retriever(settings=self._settings)
        self._generator = generator or AnswerGenerator(self._settings)

    async def stream(self, request: QueryRequest) -> AsyncIterator[QueryStreamEvent]:
        try:
            detected = self._resolve_language(request)
            yield QueryStreamEvent(type="metadata", detected_language=detected)

            language_filter: str | None = None
            if request.language and request.language != "auto":
                language_filter = request.language

            chunks = self._retriever.retrieve(
                request.query,
                top_k=request.top_k,
                language=language_filter,
            )
            yield QueryStreamEvent(type="chunks", chunks=chunks)

            chunk_ids = [c.id for c in chunks]
            graph_context = await get_graph_context(chunk_ids)

            answer_parts: list[str] = []
            async for token in self._generator.stream_answer(
                request.query, chunks, detected, graph_context
            ):
                answer_parts.append(token)
                yield QueryStreamEvent(type="token", token=token)

            yield QueryStreamEvent(type="done", answer="".join(answer_parts))
        except Exception as exc:
            logger.exception("rag_chain_failed", error=str(exc))
            yield QueryStreamEvent(type="error", error=str(exc))

    def _resolve_language(self, request: QueryRequest) -> LanguageCode:
        if request.language and request.language != "auto":
            return request.language
        return detect_language(request.query, self._settings)
