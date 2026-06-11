"""HTML parser that strips markup and returns visible text (stdlib html.parser)."""

from html.parser import HTMLParser as _StdHTMLParser

from app.ingestion.parsers.base import BaseParser

_SKIP_TAGS = {"script", "style", "head", "meta", "link"}


class _TextExtractor(_StdHTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            stripped = data.strip()
            if stripped:
                self._parts.append(stripped)

    @property
    def text(self) -> str:
        return "\n".join(self._parts).strip()


class HTMLParser(BaseParser):
    def parse(self, file_path: str) -> str:
        """Parse an HTML document and return its visible text."""
        with open(file_path, encoding="utf-8", errors="ignore") as handle:
            extractor = _TextExtractor()
            extractor.feed(handle.read())
            return extractor.text
