"""All Cypher query strings (parameterised)."""

MERGE_DOCUMENT = """
MERGE (d:Document {id: $doc_id})
ON CREATE SET
    d.title = $title,
    d.language = $language,
    d.source_url = $source_url,
    d.celex_id = $celex_id,
    d.ingested_at = datetime()
"""

MERGE_CHUNK = """
MATCH (d:Document {id: $doc_id})
MERGE (c:Chunk {id: $chunk_id})
ON CREATE SET
    c.text = $text,
    c.embedding_id = $embedding_id,
    c.chunk_index = $chunk_index,
    c.token_count = $token_count,
    c.language = $language
MERGE (d)-[:HAS_CHUNK]->(c)
"""

MERGE_ENTITY = """
MATCH (c:Chunk {id: $chunk_id})
MERGE (e:Entity {name: $entity_name, type: $entity_type})
ON CREATE SET
    e.id = $entity_id,
    e.language = $language
MERGE (c)-[:MENTIONS]->(e)
"""

GET_GRAPH_CONTEXT = """
MATCH (c:Chunk)
WHERE c.id IN $chunk_ids
MATCH (c)-[:MENTIONS]->(e:Entity)
MATCH (e)-[r]-(related)
RETURN e.name AS entity, type(r) AS relation, labels(related)[0] AS related_type,
       COALESCE(related.name, related.title, related.id) AS related_name
LIMIT 50
"""

GET_SUBGRAPH = """
MATCH (e:Entity {id: $entity_id})-[rels*1..2]-()
UNWIND rels AS rel
WITH DISTINCT rel
WITH startNode(rel) AS s, endNode(rel) AS t, type(rel) AS rel_type
RETURN
    {
        id: coalesce(s.id, elementId(s)),
        name: coalesce(s.name, s.title, ''),
        type: coalesce(s.type, ''),
        label: coalesce(head(labels(s)), 'Unknown')
    } AS source,
    {
        id: coalesce(t.id, elementId(t)),
        name: coalesce(t.name, t.title, ''),
        type: coalesce(t.type, ''),
        label: coalesce(head(labels(t)), 'Unknown')
    } AS target,
    rel_type
"""

GET_ALL_ENTITIES = """
MATCH (e:Entity)
RETURN e.id AS id, e.name AS name, e.type AS type, count{ (e)--() } AS degree
ORDER BY degree DESC
LIMIT 100
"""

DELETE_DOCUMENT = """
MATCH (d:Document {id: $doc_id})
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
DETACH DELETE c, d
"""
