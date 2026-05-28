# Architecture — Phase 1 Foundation

## Overview

The Multilingual Graph RAG Platform is a full-stack application with a FastAPI backend, React frontend, and four storage backends (PostgreSQL, Redis, Neo4j, Milvus).

Phase 1 establishes the foundation: containerised infrastructure, JWT authentication, health monitoring, and a React shell with protected routing.

## Layer diagram

```
┌─────────────────────────────────────────────────────────┐
│  React Frontend (Vite + Tailwind + Zustand)             │
│  LoginPage · Navbar · Protected Routes                  │
└──────────────────────┬──────────────────────────────────┘
                       │ REST /api/v1
┌──────────────────────▼──────────────────────────────────┐
│  FastAPI Backend                                        │
│  ┌──────────┐  ┌────────────┐  ┌───────────────────┐   │
│  │ Routes   │→ │ Services   │→ │ Repositories/DB   │   │
│  │ auth     │  │ AuthService│  │ UserRepository    │   │
│  │ health   │  │ HealthSvc  │  │                   │   │
│  └──────────┘  └────────────┘  └───────────────────┘   │
└──────┬──────────────┬──────────────┬────────────────────┘
       │              │              │
  PostgreSQL       Redis          Neo4j / Milvus
  (users)       (refresh tokens)  (Phase 2+)
```

## Authentication flow

1. Client POSTs `{email, password}` to `/api/v1/auth/login`
2. `AuthService` verifies credentials against PostgreSQL
3. Returns JWT access token + refresh token (refresh stored in Redis)
4. Client attaches `Authorization: Bearer <token>` on protected requests
5. On 401, client auto-refreshes via `/api/v1/auth/refresh`
6. Logout revokes refresh token from Redis

## Configuration

All settings are loaded from environment variables via Pydantic Settings (`app/core/config.py`). No hardcoded secrets — see `.env.example` for the full list.

Bootstrap admin user is created on first startup when `BOOTSTRAP_ADMIN_EMAIL` and `BOOTSTRAP_ADMIN_PASSWORD` are set and the users table is empty.

## Database schema (Phase 1)

### users

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| email | VARCHAR(255) | Unique, indexed |
| hashed_password | VARCHAR(255) | bcrypt |
| is_active | BOOLEAN | Default true |
| is_admin | BOOLEAN | Default false |
| created_at | TIMESTAMPTZ | Auto |
| updated_at | TIMESTAMPTZ | Auto |

Managed by Alembic migration `001_create_users`.

## Health checks

`GET /api/v1/health` probes all four storage backends:

| Service | Required for | Phase 1 status |
|---------|-------------|----------------|
| PostgreSQL | Auth, data | Required |
| Redis | Refresh tokens | Required |
| Neo4j | Graph queries | Infrastructure ready |
| Milvus | Vector search | Infrastructure ready |

Overall status: `healthy` (all up), `degraded` (postgres+redis up), `unhealthy` (core down).

## CI pipeline

GitHub Actions runs on every push/PR to `main`:

1. **backend-lint** — Ruff check + format, mypy strict
2. **backend-test** — pytest unit + integration
3. **frontend-lint** — ESLint, Prettier, tsc
4. **frontend-test** — Vitest

## Local development

```bash
make dev          # Full stack via Docker Compose
make dev-infra    # Infrastructure only
make test         # All tests
make lint         # All linters
```
