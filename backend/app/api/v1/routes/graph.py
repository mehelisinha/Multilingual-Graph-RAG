"""Graph API routes for visualization."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.db.models.user import User
from app.dependencies import get_current_user
from app.graph.cypher_queries import GET_ALL_ENTITIES, GET_SUBGRAPH
from app.graph.neo4j_client import neo4j_client

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/entities")
async def get_entities(
    _: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Get top 100 entities by degree for graph visualization."""
    try:
        results = await neo4j_client.execute_query(GET_ALL_ENTITIES)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/subgraph/{entity_id}")
async def get_subgraph(
    entity_id: str,
    _: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get 2-hop neighborhood for a specific entity."""
    try:
        results = await neo4j_client.execute_query(GET_SUBGRAPH, {"entity_id": entity_id})
        nodes: dict[str, dict[str, Any]] = {}
        edges: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str]] = set()
        for record in results:
            source = record["source"]
            target = record["target"]
            rel_type = record["rel_type"]
            nodes[source["id"]] = source
            nodes[target["id"]] = target
            key = (source["id"], rel_type, target["id"])
            if key not in seen:
                seen.add(key)
                edges.append({"source": source["id"], "target": target["id"], "type": rel_type})

        return {"nodes": list(nodes.values()), "links": edges}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
