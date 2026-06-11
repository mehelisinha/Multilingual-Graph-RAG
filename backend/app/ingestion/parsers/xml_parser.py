"""EUR-Lex Formex / generic XML parser (stdlib ElementTree)."""

from xml.etree import ElementTree as ET

from app.ingestion.parsers.base import BaseParser


class XMLParser(BaseParser):
    def parse(self, file_path: str) -> str:
        """Parse an XML document and return its concatenated text content."""
        tree = ET.parse(file_path)  # noqa: S314 - trusted local upload, no network entities
        root = tree.getroot()
        parts = [text.strip() for text in root.itertext() if text and text.strip()]
        return "\n".join(parts).strip()
