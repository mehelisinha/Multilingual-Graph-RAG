"""LLM answer generation with Ollama streaming and grounded fallback."""

import json
from collections.abc import AsyncIterator

import httpx

from app.api.v1.schemas.query import ChunkResult
from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.pipeline.constants import LanguageCode

logger = get_logger(__name__)

_LANGUAGE_NAMES: dict[LanguageCode, str] = {
    "de": "German",
    "en": "English",
    "fr": "French",
    "pl": "Polish",
}


def build_prompt(
    query: str,
    chunks: list[ChunkResult],
    answer_language: LanguageCode,
    graph_context: str = "",
) -> str:
    lang_name = _LANGUAGE_NAMES.get(answer_language, "English")
    context_blocks = []
    for index, chunk in enumerate(chunks, start=1):
        context_blocks.append(
            f"[{index}] ({chunk.language.upper()}) {chunk.title}\n{chunk.text[:1200]}"
        )
    context = "\n\n".join(context_blocks) if context_blocks else "No relevant documents found."
    return (
        f"You are a multilingual legal research assistant. Answer in {lang_name}.\n"
        "Use only the provided context. Cite sources as [1], [2], etc.\n\n"
        f"Context:\n{context}\n\n"
        f"{graph_context}\n\n"
        f"Question: {query}\n\n"
        "Answer:"
    )


def _fallback_answer(query: str, chunks: list[ChunkResult], answer_language: LanguageCode) -> str:
    if not chunks:
        return "No relevant documents were found for your query."
    lang_name = _LANGUAGE_NAMES.get(answer_language, "English")
    lines = [f"Summary ({lang_name}) based on retrieved sources:\n"]
    for index, chunk in enumerate(chunks[:5], start=1):
        excerpt = chunk.text[:280].rstrip()
        if len(chunk.text) > 280:
            excerpt += "..."
        lines.append(f"[{index}] {chunk.title} ({chunk.language.upper()}): {excerpt}")
    lines.append(f"\nQuery: {query}")
    return "\n".join(lines)


class AnswerGenerator:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    async def stream_answer(
        self,
        query: str,
        chunks: list[ChunkResult],
        answer_language: LanguageCode,
        graph_context: str = "",
    ) -> AsyncIterator[str]:
        prompt = build_prompt(query, chunks, answer_language, graph_context)
        streamed = False
        async for token in self._stream_ollama(prompt):
            streamed = True
            yield token

        if not streamed:
            for char in _fallback_answer(query, chunks, answer_language):
                yield char

    async def _stream_ollama(self, prompt: str) -> AsyncIterator[str]:
        if self._settings.llm_provider != "ollama":
            return
        url = f"{self._settings.ollama_base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self._settings.ollama_model,
            "prompt": prompt,
            "stream": True,
        }
        try:
            async with (
                httpx.AsyncClient(timeout=120.0) as client,
                client.stream("POST", url, json=payload) as response,
            ):
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    data = json.loads(line)
                    token = data.get("response", "")
                    if token:
                        yield token
                    if data.get("done"):
                        break
        except Exception as exc:
            logger.warning("ollama_stream_failed", error=str(exc))
