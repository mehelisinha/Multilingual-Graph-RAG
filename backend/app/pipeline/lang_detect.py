"""Language detection via fastText with langdetect fallback."""

from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.pipeline.constants import SUPPORTED_LANGUAGES, LanguageCode

logger = get_logger(__name__)

_FASTTEXT_LABEL_PREFIX = "__label__"


@lru_cache(maxsize=1)
def _load_fasttext(model_path_str: str) -> Any | None:
    model_path = Path(model_path_str)
    if not model_path.is_file():
        return None
    try:
        import fasttext

        return fasttext.load_model(str(model_path))
    except Exception as exc:
        logger.warning("fasttext_load_failed", error=str(exc))
        return None


def _normalize_code(raw: str) -> LanguageCode | None:
    code = raw.lower().strip()[:2]
    if code in SUPPORTED_LANGUAGES:
        return code
    return None


def _detect_with_fasttext(text: str, settings: Settings) -> LanguageCode | None:
    model = _load_fasttext(settings.fasttext_model_path)
    if model is None:
        return None
    labels, _ = model.predict(text.replace("\n", " ")[:1000])
    label = labels[0]
    if label.startswith(_FASTTEXT_LABEL_PREFIX):
        label = label[len(_FASTTEXT_LABEL_PREFIX) :]
    return _normalize_code(label)


def _detect_with_langdetect(text: str) -> LanguageCode | None:
    try:
        from langdetect import DetectorFactory, detect

        DetectorFactory.seed = 0
        return _normalize_code(detect(text))
    except Exception:
        return None


def detect_language(text: str, settings: Settings | None = None) -> LanguageCode:
    """Detect language for a query or passage; defaults to English."""
    cfg = settings or get_settings()
    stripped = text.strip()
    if not stripped:
        return "en"

    detected = _detect_with_fasttext(stripped, cfg) or _detect_with_langdetect(stripped)
    return detected or "en"
