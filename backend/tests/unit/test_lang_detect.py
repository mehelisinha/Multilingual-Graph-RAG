"""Language detection tests."""

from unittest.mock import MagicMock, patch

from app.core.config import Settings
from app.pipeline.lang_detect import detect_language


def test_detect_language_uses_fasttext_when_available(test_settings: Settings) -> None:
    mock_model = MagicMock()
    mock_model.predict.return_value = (["__label__de"], [0.99])
    with patch("app.pipeline.lang_detect._load_fasttext", return_value=mock_model):
        assert detect_language("Datenschutz und GDPR", test_settings) == "de"


def test_detect_language_falls_back_to_english(test_settings: Settings) -> None:
    with (
        patch("app.pipeline.lang_detect._load_fasttext", return_value=None),
        patch("app.pipeline.lang_detect._detect_with_langdetect", return_value=None),
    ):
        assert detect_language("???", test_settings) == "en"
