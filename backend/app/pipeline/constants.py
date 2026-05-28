"""Shared pipeline constants."""

from typing import Literal

LanguageCode = Literal["de", "en", "fr", "pl"]

SUPPORTED_LANGUAGES: tuple[LanguageCode, ...] = ("de", "en", "fr", "pl")

E5_QUERY_PREFIX = "query: "
E5_PASSAGE_PREFIX = "passage: "

DEFAULT_TOP_K = 10
MIN_TOP_K = 1
MAX_TOP_K = 20

# Rough token budget: ~4 chars per token, target 256-512 tokens per chunk
TARGET_CHUNK_CHARS = 1800
MAX_CHUNK_CHARS = 2400
MIN_CHUNK_CHARS = 200
