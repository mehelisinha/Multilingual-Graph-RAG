"""Embedder tests."""

from unittest.mock import MagicMock, patch

import numpy as np

from app.pipeline.constants import E5_PASSAGE_PREFIX, E5_QUERY_PREFIX
from app.pipeline.embedder import Embedder


def test_embedder_prefixes_query_and_passages(test_settings) -> None:
    mock_model = MagicMock()
    mock_model.encode.side_effect = [
        np.array([1.0, 0.0]),
        np.array([[1.0, 0.0], [0.0, 1.0]]),
    ]

    with patch("app.pipeline.embedder._get_model", return_value=mock_model):
        embedder = Embedder(test_settings)
        query_vec = embedder.embed_query("GDPR")
        passage_vecs = embedder.embed_passages(["Article 17", "Article 18"])

    mock_model.encode.assert_any_call(
        f"{E5_QUERY_PREFIX}GDPR",
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    mock_model.encode.assert_any_call(
        [f"{E5_PASSAGE_PREFIX}Article 17", f"{E5_PASSAGE_PREFIX}Article 18"],
        normalize_embeddings=True,
        show_progress_bar=False,
        batch_size=32,
    )
    assert query_vec == [1.0, 0.0]
    assert len(passage_vecs) == 2
