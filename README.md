# Multilingual Graph RAG Platform

Enterprise knowledge intelligence system combining multilingual retrieval-augmented generation (RAG), knowledge graph reasoning, and a React web frontend.

## Stack

- **Backend:** FastAPI, Celery, SQLAlchemy
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS
- **Storage:** Milvus (vectors), Neo4j (graph), PostgreSQL (relational), Redis (cache/queue)
- **Embedding:** multilingual-e5-large
- **Target languages:** German, English, French, Polish

## Project structure

```
multilingual-graph-rag/
├── backend/          # FastAPI application
├── frontend/         # React/TypeScript UI
├── data/             # Datasets and ingestion scripts
├── infra/            # Docker, nginx, monitoring, k8s
├── docs/             # Architecture, API, deployment docs
└── .github/          # CI/CD workflows
```

See [docs/architecture.md](docs/architecture.md) and the PRD (`multilingual_graph_rag_PRD.pdf`) for full specifications.

## Getting started

```bash
cp .env.example .env.local
docker compose up -d
make dev
```

Detailed setup instructions will be added in Phase 1.

## License

Personal portfolio project — Meheli Sinha
