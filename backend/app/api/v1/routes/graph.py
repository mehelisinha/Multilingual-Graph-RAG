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
        results = await neo4j_client.execute_query(
            GET_SUBGRAPH, {"entity_id": entity_id}
        )
        nodes = {}
        edges = []
        for record in results:
            e = record.get("e")
            r = record.get("r")
            n = record.get("n")
            if e:
                nodes[e.get("id")] = {
                    "id": e.get("id"),
                    "name": e.get("name"),
                    "type": e.get("type"),
                    "label": next(iter(e.labels)) if e.labels else "Entity",
                }
            if n and hasattr(n, "labels"):
                label = next(iter(n.labels)) if n.labels else "Unknown"
                nodes[n.get("id", str(n.element_id))] = {
                    "id": n.get("id", str(n.element_id)),
                    "name": n.get("name") or n.get("title", ""),
                    "type": n.get("type", ""),
                    "label": label,
                }

            if isinstance(r, list):
                for rel in r:
                    edges.append(
                        {
                            "source": rel.nodes[0].get("id", str(rel.nodes[0].element_id)),
                            "target": rel.nodes[1].get("id", str(rel.nodes[1].element_id)),
                            "type": rel.type,
                        }
                    )
            elif r:
                edges.append(
                    {
                        "source": rel.nodes[0].get("id", str(rel.nodes[0].element_id)),
                        "target": rel.nodes[1].get("id", str(rel.nodes[1].element_id)),
                        "type": rel.type,
                    }
                )

        # Deduplicate edges
        unique_edges = []
        seen = set()
        for edge in edges:
            key = f"{edge['source']}-{edge['type']}-{edge['target']}"
            if key not in seen:
                seen.add(key)
                unique_edges.append(edge)

        return {"nodes": list(nodes.values()), "links": unique_edges}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
