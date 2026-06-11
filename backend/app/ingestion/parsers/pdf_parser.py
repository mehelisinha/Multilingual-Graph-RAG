"""PDF parser using PyMuPDF."""

from app.ingestion.parsers.base import BaseParser


class PDFParser(BaseParser):
    def parse(self, file_path: str) -> str:
        """Parse PDF and extract text."""
        # Imported lazily so the app boots even if PyMuPDF is not installed;
        # only an actual PDF upload requires it.
        import fitz

        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text() + "\n"
        return text.strip()
