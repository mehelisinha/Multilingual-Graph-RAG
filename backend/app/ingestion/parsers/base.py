"""Abstract parser interface."""

from abc import ABC, abstractmethod


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> str:
        """Parse the file and return extracted text."""
        pass
