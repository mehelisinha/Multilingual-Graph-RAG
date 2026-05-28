"""Pipeline domain types shared across ingestion and retrieval."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    document_id: str
    chunk_index: int
    text: str
    language: str
    title: str

    @property
    def chunk_id(self) -> str:
        return f"{self.document_id}:{self.chunk_index}"
