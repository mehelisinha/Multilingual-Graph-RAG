"""multilingual-e5-large embedding wrapper with a dependency-free fallback."""

import hashlib
import re
from functools import lru_cache
from typing import TYPE_CHECKING, Any

import numpy as np

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.pipeline.constants import E5_PASSAGE_PREFIX, E5_QUERY_PREFIX

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

logger = get_logger(__name__)

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


@lru_cache(maxsize=1)
def _get_model(model_name: str) -> "SentenceTransformer | None":
    """Load the sentence-transformer, or return None if the ml extra is unavailable."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        logger.warning("sentence_transformers_unavailable_using_hash_embedder")
        return None
    logger.info("loading_embedding_model", model=model_name)
    return SentenceTransformer(model_name)


def _hash_embed(text: str, dim: int) -> list[float]:
    """Deterministic hashing-trick embedding; a low-quality stand-in for a real model.

    Shared tokens map to shared dimensions, so lexically similar texts get similar
    vectors — enough for the pipeline to run without torch/sentence-transformers.
    """
    vector = np.zeros(dim, dtype=np.float64)
    tokens = _TOKEN_RE.findall(text.lower())
    for token in tokens:
        digest = hashlib.md5(token.encode("utf-8"), usedforsecurity=False).digest()
        bucket = int.from_bytes(digest[:8], "little") % dim
        sign = 1.0 if digest[8] & 1 else -1.0
        vector[bucket] += sign
    norm = float(np.linalg.norm(vector))
    if norm == 0.0:
        vector[0] = 1.0
        norm = 1.0
    return [float(value) for value in vector / norm]


class Embedder:
    """Lazy-loaded sentence-transformer for mE5 embeddings, with a hashing fallback."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    @property
    def _model(self) -> "SentenceTransformer | None":
        return _get_model(self._settings.embedding_model)

    def _encode(self, value: Any, *, batch_size: int | None = None) -> Any:
        model = self._model
        assert model is not None, "_encode requires a loaded model; callers must check first"
        kwargs: dict[str, Any] = {"normalize_embeddings": True, "show_progress_bar": False}
        if batch_size is not None:
            kwargs["batch_size"] = batch_size
        return model.encode(value, **kwargs)

    def embed_query(self, text: str) -> list[float]:
        if self._model is None:
            return _hash_embed(text, self.dimension)
        vector = self._encode(f"{E5_QUERY_PREFIX}{text}")
        return list(np.asarray(vector).tolist())

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if self._model is None:
            return [_hash_embed(text, self.dimension) for text in texts]
        prefixed = [f"{E5_PASSAGE_PREFIX}{text}" for text in texts]
        vectors = self._encode(prefixed, batch_size=32)
        return [list(row) for row in np.asarray(vectors).tolist()]

    @property
    def dimension(self) -> int:
        return self._settings.embedding_dimension
