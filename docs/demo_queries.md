# Demo Queries

This document contains sample queries to test the Multilingual Graph RAG platform across various languages and domains, assuming the sample data or relevant documents have been ingested.

## Basic Information Retrieval (English)
1. **Query**: "What are the core regulations surrounding data privacy in the EU?"
   - **Expected Behavior**: Retrieves documents containing GDPR text, reranks them using the Cross-Encoder, and generates a structured summary.
2. **Query**: "Who is the CEO of Google?"
   - **Expected Behavior**: Utilizes Neo4j Knowledge Graph to find the relationship `(Person: Sundar Pichai) -[CEO_OF]-> (Organization: Google)` and incorporates it into the generated response.

## Multilingual Capabilities
The system supports cross-lingual retrieval. You can query in one language to retrieve documents originally written in another.

### German Queries
1. **Query**: "Was sind die wichtigsten Umweltschutzgesetze?"
   - *Translation: "What are the most important environmental protection laws?"*
   - **Expected Behavior**: Detects German, embeds the query using `mE5`, retrieves German and English documents, and generates a response in German.
2. **Query**: "Wer ist der Präsident von Frankreich?"
   - *Translation: "Who is the president of France?"*

### Spanish Queries
1. **Query**: "¿Cuáles son los requisitos para obtener una visa de trabajo?"
   - *Translation: "What are the requirements to obtain a work visa?"*
2. **Query**: "¿Cómo afecta la inflación a la economía global?"
   - *Translation: "How does inflation affect the global economy?"*

## Graph Reasoning
Queries that require multi-hop reasoning across entities extracted from different documents.

1. **Query**: "How are the organizations mentioned in the recent climate summit related to each other?"
   - **Expected Behavior**: Queries Neo4j for relationships between organizations, providing context that standard vector search might miss.
2. **Query**: "List all individuals associated with the 'Project Apollo' and their respective roles."
