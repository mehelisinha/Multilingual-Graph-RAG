# Multilingual Graph RAG Platform

Enterprise knowledge intelligence system combining multilingual retrieval-augmented generation (RAG), knowledge graph reasoning, and a React web frontend.

## Stack

- **Backend:** FastAPI, SQLAlchemy 2.0 (async), Alembic, JWT auth, Redis
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Zustand, React Router
- **Storage:** PostgreSQL, Redis, Neo4j, Milvus (vector retrieval active in Phase 2)
- **DevOps:** Docker Compose, GitHub Actions CI, Ruff, mypy, ESLint, Prettier

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

## Phase 2 — Load sample data and query

```bash
# Download MultiEURLEX sample (requires HuggingFace `datasets`)
cd backend && pip install -r requirements-dev.txt
python ../data/scripts/download_multieurlex.py --sample 200

# Index into Milvus (Milvus must be running: make dev-infra)
python ../data/scripts/ingest_to_milvus.py

# Optional: fastText language model (~900MB)
mkdir -p models
curl -L -o models/lid.176.bin https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
```

Use the **Search** page at http://localhost:5173 to run cross-lingual queries. The API streams results via SSE at `POST /api/v1/query`.

## API endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/login` | Public | Login with email/password |
| POST | `/api/v1/auth/refresh` | Public | Refresh access token |
| POST | `/api/v1/auth/logout` | Public | Revoke refresh token |
| GET | `/api/v1/auth/me` | JWT | Current user profile |
| POST | `/api/v1/query` | JWT | Multilingual RAG query (SSE stream) |
| GET | `/api/v1/health` | Public | Service health check |
| GET | `/api/v1/metrics` | Public | Prometheus metrics |

## Project structure

```
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/      # Route handlers + Pydantic schemas
│   │   ├── core/     # Config, security, middleware, logging
│   │   ├── db/       # SQLAlchemy models, migrations, Redis
│   │   └── services/ # Business logic layer
│   └── tests/
├── frontend/         # React/TypeScript UI
├── data/             # Dataset scripts (Phase 2+)
├── infra/            # Nginx, monitoring, k8s
└── docs/             # Architecture and API docs
```

## Phase roadmap

| Phase | Status | Deliverables |
|-------|--------|--------------|
| **1 — Foundation** | Complete | Docker stack, FastAPI skeleton, JWT auth, React scaffold, CI |
| **2 — Multilingual RAG** | Complete | mE5 embeddings, Milvus, fastText/langdetect, query SSE, SearchPage |
| 3 — Graph Layer | Planned | Neo4j NER, graph traversal, GraphViewer |
| 4 — Ingestion UI | Planned | Upload, Celery pipeline, Admin dashboard |
| 5 — Production | Planned | Reranker, Cloud Run deploy, E2E tests |

See [docs/architecture.md](docs/architecture.md) and `multilingual_graph_rag_PRD.pdf` for full specifications.

## License

Personal portfolio project — Meheli Sinha
