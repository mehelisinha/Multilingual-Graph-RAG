"""Ingestion entry point: dispatch a file to the correct parser by extension."""

import os

from app.ingestion.parsers import BaseParser, HTMLParser, PDFParser, XMLParser

_PARSERS: dict[str, type[BaseParser]] = {
    ".pdf": PDFParser,
    ".xml": XMLParser,
    ".html": HTMLParser,
    ".htm": HTMLParser,
}

SUPPORTED_EXTENSIONS = tuple(_PARSERS.keys())


class UnsupportedFileTypeError(ValueError):
    """Raised when an uploaded file has no registered parser."""


def process_file_to_text(file_path: str) -> str:
    """Parse a file to raw text based on its extension."""
    ext = os.path.splitext(file_path)[1].lower()
    parser_cls = _PARSERS.get(ext)
    if parser_cls is None:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{ext}'. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    return parser_cls().parse(file_path)
