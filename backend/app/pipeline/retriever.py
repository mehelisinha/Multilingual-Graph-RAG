"""Milvus ANN retrieval service."""

from app.api.v1.schemas.query import ChunkResult
from app.core.config import Settings, get_settings
from app.db.milvus import MilvusStore
from app.pipeline.embedder import Embedder


def _normalize_score(raw_distance: float) -> float:
    """Map Milvus cosine distance to a 0-1 relevance score (higher is better)."""
    # Milvus cosine distance is in [0, 2]; similarity ≈ 1 - distance for normalized vectors
    return max(0.0, min(1.0, 1.0 - raw_distance))


class Retriever:
    def __init__(
        self,
        embedder: Embedder | None = None,
        store: MilvusStore | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._embedder = embedder or Embedder(self._settings)
        self._store = store or MilvusStore(self._settings)

    def retrieve(
        self,
        query: str,
        *,
        top_k: int | None = None,
        language: str | None = None,
    ) -> list[ChunkResult]:
        limit = top_k or self._settings.default_top_k
        query_vector = self._embedder.embed_query(query)
        hits = self._store.search(query_vector, top_k=limit, language=language)
        return [
            ChunkResult(
                id=str(hit.get("id", "")),
                document_id=str(hit.get("document_id", "")),
                chunk_index=int(hit.get("chunk_index", 0)),
                text=str(hit.get("text", "")),
                language=str(hit.get("language", "")),
                title=str(hit.get("title", "")),
                score=_normalize_score(float(hit.get("score", 0.0))),
            )
            for hit in hits
        ]
