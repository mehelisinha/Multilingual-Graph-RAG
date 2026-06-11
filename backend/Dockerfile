FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/

FROM base AS development

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
# ml extra (torch/sentence-transformers) is omitted: its torch wheel is served from a
# separate index that the build network blocks. The app falls back to a hashing embedder.
RUN uv sync --frozen --group dev --no-install-project
COPY . .
RUN uv sync --frozen --group dev
# Multilingual + German NER models used by the ingestion pipeline.
# Non-fatal: if the network blocks the model wheels, NER degrades to empty
# entities at runtime rather than failing the image build.
RUN uv run python -m spacy download xx_ent_wiki_sm \
    && uv run python -m spacy download de_core_news_sm \
    || echo "spaCy model download failed; NER will be disabled at runtime"

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS production

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --extra ml --no-dev --no-install-project
COPY . .
RUN uv sync --frozen --extra ml --no-dev

EXPOSE 8000

CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
