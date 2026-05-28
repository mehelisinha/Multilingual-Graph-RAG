"""multilingual-e5-large embedding wrapper."""

from functools import lru_cache
from typing import TYPE_CHECKING

import numpy as np

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.pipeline.constants import E5_PASSAGE_PREFIX, E5_QUERY_PREFIX

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _get_model(model_name: str) -> "SentenceTransformer":
    from sentence_transformers import SentenceTransformer

    logger.info("loading_embedding_model", model=model_name)
    return SentenceTransformer(model_name)


class Embedder:
    """Lazy-loaded sentence-transformer for mE5 embeddings."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    @property
    def model(self) -> "SentenceTransformer":
        return _get_model(self._settings.embedding_model)

    def embed_query(self, text: str) -> list[float]:
        vector = self.model.encode(
            f"{E5_QUERY_PREFIX}{text}",
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return list(np.asarray(vector).tolist())

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        prefixed = [f"{E5_PASSAGE_PREFIX}{text}" for text in texts]
        vectors = self.model.encode(
            prefixed,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32,
        )
        return [list(row) for row in np.asarray(vectors).tolist()]

    @property
    def dimension(self) -> int:
        return self._settings.embedding_dimension
