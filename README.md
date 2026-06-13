# Multilingual Graph RAG Platform

Enterprise knowledge intelligence system combining multilingual retrieval-augmented generation (RAG), knowledge graph reasoning, and a React web frontend.

## Stack

- **Backend:** FastAPI, SQLAlchemy 2.0 (async), Alembic, JWT auth, Celery, Redis
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Zustand, React Router
- **Storage:** PostgreSQL, Redis, Neo4j (knowledge graph), Milvus (vector search)
- **ML/NLP:** mE5 embeddings, spaCy NER, cross-encoder reranker, fastText/langdetect
- **DevOps:** Docker Compose, Nginx, GitHub Actions (CI + image publishing), Prometheus, Grafana, Ruff, mypy, ESLint, Prettier

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommended — runs all services)
- Python 3.12+ (for local backend development without Docker)
- Node.js 20+ (for local frontend development without Docker)

## Quick start (Docker — recommended)

```bash
# 1. Clone and configure
git clone https://github.com/mehelisinha/Multilingual-Graph-RAG.git
cd Multilingual-Graph-RAG
cp .env.example .env.local

# 2. Start the full stack (Postgres, Redis, Neo4j, Milvus, backend, frontend)
make dev

# 3. Open the app
# Frontend:  http://localhost:5173
# API docs:  http://localhost:8000/docs
# Neo4j UI:  http://localhost:7474
```

**Default login** (created automatically on first startup if no users exist):

| Field | Value |
|-------|-------|
| Email | `admin@example.com` |
| Password | `changeme123` |

Override via `BOOTSTRAP_ADMIN_EMAIL` and `BOOTSTRAP_ADMIN_PASSWORD` in `.env.local`.

## Local development (without Docker for app code)

```bash
# Start infrastructure only
make dev-infra

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example ../.env.local
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Production deployment

`docker-compose.prod.yml` brings up the whole platform behind Nginx, which serves
the built frontend and reverse-proxies the API (including the ingestion WebSocket).
The stack also runs a dedicated Celery worker for document ingestion and a
Prometheus + Grafana pair for metrics.

```bash
# Build and start the production stack
docker-compose -f docker-compose.prod.yml up -d --build

# Tail the logs
docker-compose -f docker-compose.prod.yml logs -f
```

Once it's up:

- App (frontend + API): `http://localhost`
- Grafana dashboards: `http://localhost:3000` (admin password from `GRAFANA_ADMIN_PASSWORD`, defaults to `admin`)

A couple of things to set before exposing this to the internet: `SECRET_KEY` must be
a real value (the app refuses to boot in production with the bundled dev key), and
you'll want to put TLS termination in front of Nginx. Setting `SENTRY_DSN` turns on
error reporting; leaving it empty keeps Sentry off.

Pushes to `main` build the backend and frontend images and publish them to GitHub
Container Registry (`ghcr.io/mehelisinha/multilingual-graph-rag-{backend,frontend}`),
so you can pull tagged images instead of building on the host.

## Production readiness

Where the platform stands today, layer by layer:

| Area | Status | Notes |
|------|--------|-------|
| Frontend | ✅ | React + Vite SPA, built and served as static assets |
| API & backend logic | ✅ | Async FastAPI, Celery workers, streaming RAG pipeline |
| Database & storage | ✅ | Postgres + Alembic, Redis, Neo4j, Milvus on persistent volumes |
| Auth & permissions | ✅ | JWT access/refresh, hashed passwords, admin-only upload and delete |
| Security headers | ✅ | nosniff/frame/referrer on every response, HSTS outside dev, Nginx mirrors them |
| CI / CD | ✅ | Lint, type-check and tests on every PR; images published to GHCR on merge |
| Observability | ✅ | Structured logs with request IDs, Prometheus `/metrics`, Grafana dashboard, optional Sentry |
| Caching | ◐ | Redis for sessions and model caches; no HTTP response cache or CDN yet |
| Rate limiting | ✗ | Not implemented |
| Horizontal scaling / LB | ◐ | Celery scales by replica count; single backend instance otherwise |
| Backups & recovery | ✗ | Relies on Docker volumes; no automated backups yet |

The unchecked items are the natural next steps if this moves to real traffic.

## Available commands

| Command | Description |
|---------|-------------|
| `make dev` | Start full Docker Compose stack |
| `make dev-infra` | Start Postgres, Redis, Neo4j, Milvus only |
| `make stop` | Stop all containers |
| `make migrate` | Run Alembic migrations |
| `make lint` | Run Ruff + ESLint + Prettier checks |
| `make test` | Run pytest + Vitest |
| `make typecheck` | Run mypy + tsc |

## Load sample data and query

```bash
# Download MultiEURLEX sample (requires HuggingFace `datasets`)
cd backend && pip install -r requirements-dev.txt
python ../data/scripts/download_multieurlex.py --sample 200

# Alternative if the HuggingFace CDN is blocked: fetch directly from EUR-Lex
python ../data/scripts/download_eurlex_corpus.py

# Index into Milvus (Milvus must be running: make dev-infra)
python ../data/scripts/ingest_to_milvus.py

# Build the Neo4j knowledge graph (powers Graph Explorer and graph-enriched answers)
python ../data/scripts/build_graph.py

# Optional: fastText language model (~900MB)
mkdir -p models
curl -L -o models/lid.176.bin https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
```

Use the **Search** page at http://localhost:5173 to run cross-lingual queries (results stream via SSE at `POST /api/v1/query`), and the **Graph Explorer** page to browse the knowledge graph around any entity. See [docs/data_pipeline.md](docs/data_pipeline.md) for the full pipeline reference.

## API endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/login` | Public | Login with email/password |
| POST | `/api/v1/auth/refresh` | Public | Refresh access token |
| POST | `/api/v1/auth/logout` | Public | Revoke refresh token |
| GET | `/api/v1/auth/me` | JWT | Current user profile |
| POST | `/api/v1/query` | JWT | Multilingual RAG query (SSE stream) |
| GET | `/api/v1/query/history` | JWT | Recent queries of the current user |
| GET | `/api/v1/graph/entities` | JWT | Top entities by degree (Graph Explorer sidebar) |
| GET | `/api/v1/graph/subgraph/{entity_id}` | JWT | 2-hop neighborhood of an entity |
| POST | `/api/v1/ingest` | Admin | Upload a document (PDF/HTML/XML) for ingestion |
| GET | `/api/v1/ingest/{job_id}` | JWT | Ingestion job status |
| WS | `/api/v1/ingest/ws/{job_id}` | JWT | Live ingestion progress updates |
| GET | `/api/v1/documents` | JWT | List ingested documents |
| DELETE | `/api/v1/documents/{document_id}` | Admin | Delete a document and its chunks |
| GET | `/api/v1/health` | Public | Service health check |
| GET | `/api/v1/metrics` | Public | Prometheus metrics |

## Project structure

```
├── backend/            # FastAPI application
│   ├── app/
│   │   ├── api/        # Route handlers + Pydantic schemas
│   │   ├── core/       # Config, security, middleware, logging
│   │   ├── db/         # SQLAlchemy models, migrations, Redis, Milvus
│   │   ├── graph/      # Neo4j client, Cypher queries, graph builder
│   │   ├── ingestion/  # Parsers, chunker, NER, ingestion pipeline
│   │   ├── pipeline/   # RAG chain: embedder, retriever, reranker
│   │   ├── services/   # Business logic layer
│   │   └── workers/    # Celery app and tasks
│   └── tests/
├── frontend/           # React/TypeScript UI
├── data/               # Corpus download / indexing / graph scripts
├── infra/              # Nginx, monitoring, k8s
└── docs/               # Architecture and API docs
```

## Phase roadmap

| Phase | Status | Deliverables |
|-------|--------|--------------|
| **1 — Foundation** | Complete | Docker stack, FastAPI skeleton, JWT auth, React scaffold, CI |
| **2 — Multilingual RAG** | Complete | mE5 embeddings, Milvus, fastText/langdetect, query SSE, SearchPage |
| **3 — Graph Layer** | Complete | Neo4j NER, graph traversal, GraphViewer |
| **4 — Ingestion UI** | Complete | Upload, Celery pipeline, Admin dashboard |
| **5 — Production** | Complete | Reranker, admin RBAC, security headers, monitoring, GHCR image publishing |

See [docs/architecture.md](docs/architecture.md) and `multilingual_graph_rag_PRD.pdf` for full specifications.

## License

Personal portfolio project — Meheli Sinha
