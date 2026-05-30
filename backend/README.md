# Multilingual Graph RAG — Backend

Python 3.12 · [uv](https://docs.astral.sh/uv/) for dependencies.

## Setup

```bash
# Install uv: https://docs.astral.sh/uv/getting-started/installation/

uv sync --group dev --extra ml
```

## Commands (from this directory)

| Command | Description |
|---------|-------------|
| `uv sync --group dev --extra ml` | Full local environment |
| `uv sync --group ci` | CI-equivalent (no ML stack) |
| `uv run uvicorn app.main:app --reload --port 8000` | Dev server |
| `uv run alembic upgrade head` | Migrations |
| `uv run pytest` | Tests |
| `uv run ruff check .` | Lint |
| `uv run mypy --config-file mypy.ini app` | Type check |
