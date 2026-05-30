"""Fetch graph context for retrieved chunks."""

import structlog

from app.graph.cypher_queries import GET_GRAPH_CONTEXT
from app.graph.neo4j_client import neo4j_client

logger = structlog.get_logger(__name__)


async def get_graph_context(chunk_ids: list[str]) -> str:
    """Retrieve structured graph context string for a list of chunk IDs."""
    if not chunk_ids:
        return ""

    try:
        results = await neo4j_client.execute_query(GET_GRAPH_CONTEXT, {"chunk_ids": chunk_ids})
        if not results:
            return ""

        context_lines = []
        for record in results:
            entity = record.get("entity", "")
            relation = record.get("relation", "")
            related_name = record.get("related_name", "")
            if entity and relation and related_name:
                context_lines.append(f"{entity} {relation} {related_name}")

        if context_lines:
            return "Graph Knowledge:\n" + "\n".join(context_lines)
        return ""
    except Exception as e:
        logger.error("Error fetching graph context", error=str(e))
        return ""
