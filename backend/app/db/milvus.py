"""Milvus vector store client and collection management."""

from functools import lru_cache
from typing import Any

from pymilvus import MilvusClient

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.pipeline.types import TextChunk

logger = get_logger(__name__)

_OUTPUT_FIELDS = ("document_id", "chunk_index", "text", "language", "title")


@lru_cache(maxsize=4)
def _get_client(uri: str) -> MilvusClient:
    return MilvusClient(uri=uri)


class MilvusStore:
    """Thin wrapper around pymilvus MilvusClient for chunk storage and ANN search."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client = _get_client(self._settings.milvus_uri)
        self._collection = self._settings.milvus_collection_name

    @property
    def collection_name(self) -> str:
        return self._collection

    def ensure_collection(self) -> None:
        if self._client.has_collection(self._collection):
            return
        self._client.create_collection(
            collection_name=self._collection,
            dimension=self._settings.embedding_dimension,
            metric_type="COSINE",
            auto_id=False,
            id_type="string",
            max_length=128,
        )
        logger.info("milvus_collection_created", collection=self._collection)

    def is_healthy(self) -> bool:
        try:
            return bool(self._client.has_collection(self._collection))
        except Exception as exc:
            logger.warning("milvus_health_check_failed", error=str(exc))
            return False

    def insert_chunks(self, chunks: list[TextChunk], embeddings: list[list[float]]) -> int:
        if not chunks:
            return 0
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings length mismatch")

        self.ensure_collection()
        rows: list[dict[str, Any]] = []
        for chunk, vector in zip(chunks, embeddings, strict=True):
            rows.append(
                {
                    "id": chunk.chunk_id,
                    "vector": vector,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.text[:65000],
                    "language": chunk.language,
                    "title": chunk.title[:1024],
                }
            )
        self._client.insert(collection_name=self._collection, data=rows)
        return len(rows)

    def search(
        self,
        query_vector: list[float],
        *,
        top_k: int,
        language: str | None = None,
    ) -> list[dict[str, Any]]:
        self.ensure_collection()
        filter_expr = f'language == "{language}"' if language else None
        results = self._client.search(
            collection_name=self._collection,
            data=[query_vector],
            limit=top_k,
            output_fields=list(_OUTPUT_FIELDS),
            filter=filter_expr,
        )
        hits: list[dict[str, Any]] = []
        for batch in results:
            for hit in batch:
                entity = hit.get("entity", {})
                hits.append(
                    {
                        "id": hit.get("id"),
                        "score": float(hit.get("distance", 0.0)),
                        "document_id": entity.get("document_id", ""),
                        "chunk_index": int(entity.get("chunk_index", 0)),
                        "text": entity.get("text", ""),
                        "language": entity.get("language", ""),
                        "title": entity.get("title", ""),
                    }
                )
        return hits
