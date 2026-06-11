# Data Ingestion Pipeline

The Multilingual Graph RAG platform utilizes an asynchronous, scalable data ingestion pipeline based on Celery. The pipeline is designed to process documents (such as PDFs, HTML, XML) into a unified Knowledge Graph and Vector Database representation.

## Architecture Overview

The ingestion pipeline consists of the following components:
1. **API Layer**: Receives file uploads via `POST /api/v1/ingest`.
2. **Database Layer**: Tracks document metadata and job status in PostgreSQL (`Document` and `IngestionJob` models).
3. **Task Queue**: Celery acts as the orchestrator, with Redis serving as the message broker.
4. **Processing Pipeline**: A sequence of steps to extract, chunk, embed, and enrich text data.
5. **Storage Layer**: Output is stored in Milvus (Vector DB) and Neo4j (Graph DB).

## Pipeline Steps

When a document is uploaded, the following steps are executed asynchronously:

1. **Upload & Job Creation**: The file is saved temporarily, and an `IngestionJob` is created with a `PENDING` status. A Celery task is dispatched.
2. **Parsing**: The document is read and parsed into raw text based on its file extension (e.g., `PyMuPDF` for PDFs).
3. **Chunking**: The extracted text is split into overlapping chunks (e.g., 512 tokens, 50 token overlap).
4. **Embedding & Vector Storage**: Chunks are embedded using `mE5` models and stored in Milvus for fast semantic search.
5. **Entity Extraction (NER)**: spaCy models (e.g., `en_core_web_sm`, `de_core_news_sm`) extract named entities from each chunk.
6. **Graph Building**: Extracted entities and relationships are inserted into Neo4j, linking entities to their source chunks.
7. **Completion**: The `IngestionJob` and `Document` statuses are updated to `COMPLETED`.

## Real-time Monitoring

The frontend can track the progress of an ingestion job in real-time via WebSockets at `ws://localhost:8000/api/v1/ingest/ws/{job_id}`. The WebSocket streams status updates directly from the PostgreSQL database, providing feedback on the current processing stage (e.g., `PARSING`, `CHUNKING_AND_EMBEDDING`, `EXTRACTING_ENTITIES`, `BUILDING_GRAPH`).
