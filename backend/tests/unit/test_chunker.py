"""Semantic chunker tests."""

from app.ingestion.chunker import chunk_text


def test_chunk_text_splits_long_document() -> None:
    sentence = "This is a regulatory sentence about data protection. "
    text = sentence * 80
    chunks = chunk_text(
        text,
        document_id="doc-1",
        title="GDPR Overview",
        language="en",
    )
    assert len(chunks) > 1
    assert all(chunk.document_id == "doc-1" for chunk in chunks)
    assert all(chunk.language == "en" for chunk in chunks)


def test_chunk_text_returns_empty_for_blank_input() -> None:
    assert chunk_text("", document_id="x", title="t", language="en") == []
