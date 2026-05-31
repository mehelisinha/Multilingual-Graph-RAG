"""Integration tests for graph database queries and population logic."""

from unittest.mock import AsyncMock, patch

import pytest

from app.graph.graph_builder import build_document_graph
from app.pipeline.graph_enricher import get_graph_context


@pytest.mark.asyncio
async def test_build_document_graph_neo4j_calls() -> None:
    """Verify that build_document_graph issues the correct parameterized Cypher queries to Neo4j."""
    doc = {
        "id": "doc_1",
        "title": "Test Doc",
        "language": "en",
        "source_url": "http://example.com",
        "celex_id": "12345",
    }
    chunks = [
        {
            "id": "chunk_1",
            "text": "This is a test chunk containing Google and München.",
            "embedding_id": "chunk_1",
            "chunk_index": 0,
            "token_count": 10,
            "language": "en",
            "entities": [
                {"name": "Google", "type": "ORG"},
                {"name": "München", "type": "LOC"},
            ],
        }
    ]

    with patch(
        "app.graph.neo4j_client.neo4j_client.execute_query", new_callable=AsyncMock
    ) as mock_query:
        # Execute the builder
        await build_document_graph(doc, chunks)

        # Check call counts: 1 for doc merge, 1 for chunk merge, 2 for entity merge
        assert mock_query.call_count == 4

        # Verify query prefixes
        calls = [args[0][0] for args in mock_query.call_args_list]
        assert any("MERGE (d:Document" in c for c in calls)
        assert any("MERGE (c:Chunk" in c for c in calls)
        assert any("MERGE (e:Entity" in c for c in calls)


@pytest.mark.asyncio
async def test_get_graph_context_formatting() -> None:
    """Verify that graph context formats records correctly into a readable text chunk."""
    mock_neo4j_records = [
        {
            "entity": "GDPR",
            "relation": "AMENDS",
            "related_name": "Article 17",
        },
        {
            "entity": "Allianz SE",
            "relation": "SUBJECT_OF",
            "related_name": "doc_1",
        },
    ]

    with patch(
        "app.graph.neo4j_client.neo4j_client.execute_query",
        new_callable=AsyncMock,
        return_value=mock_neo4j_records,
    ) as mock_query:
        context = await get_graph_context(["chunk_1", "chunk_2"])

        mock_query.assert_called_once()
        assert "Graph Knowledge:" in context
        assert "GDPR AMENDS Article 17" in context
        assert "Allianz SE SUBJECT_OF doc_1" in context
