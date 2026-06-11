"""Reranker using cross-encoder/ms-marco-MiniLM-L-6-v2."""

import math
from functools import lru_cache

from app.api.v1.schemas.query import ChunkResult
from app.core.logging import get_logger

logger = get_logger(__name__)

_DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def _sigmoid(value: float) -> float:
    """Squash an unbounded cross-encoder logit into a 0-1 relevance score."""
    return 1.0 / (1.0 + math.exp(-value))


class Reranker:
    def __init__(self, model_name: str = _DEFAULT_MODEL) -> None:
        # Imported lazily so the module (and importers like rag_chain) load without
        # the optional ml extras installed.
        from sentence_transformers import CrossEncoder

        self._model = CrossEncoder(model_name)

    def rerank(self, query: str, chunks: list[ChunkResult], top_k: int) -> list[ChunkResult]:
        if not chunks:
            return []

        logger.info("reranking_chunks", count=len(chunks))
        pairs = [[query, chunk.text] for chunk in chunks]
        scores = self._model.predict(pairs)

        for chunk, score in zip(chunks, scores, strict=True):
            # Replace the ANN distance score with the normalised cross-encoder score.
            chunk.score = _sigmoid(float(score))

        ranked = sorted(chunks, key=lambda c: c.score, reverse=True)
        return ranked[:top_k]


@lru_cache
def get_reranker() -> Reranker:
    """Lazily construct the reranker so the heavy model loads on first use, not import."""
    return Reranker()
