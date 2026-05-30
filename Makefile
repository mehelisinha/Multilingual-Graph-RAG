.PHONY: dev dev-infra stop test build lint lint-fix format typecheck install-dev install-ci migrate

install-dev:
	cd backend && uv sync --group dev --extra ml --native-tls
	cd backend && uv run python -m spacy download xx_ent_wiki_sm
	cd backend && uv run python -m spacy download de_core_news_sm

install-ci:
	cd backend && uv sync --group ci
	cd backend && uv run python -m spacy download xx_ent_wiki_sm
	cd backend && uv run python -m spacy download de_core_news_sm

migrate:
	cd backend && uv run alembic upgrade head

dev-infra:
	docker compose up -d postgres redis neo4j etcd minio milvus

dev:
	docker compose up -d --build

stop:
	docker compose down

lint:
	cd backend && uv run ruff check . && uv run ruff format --check .
	cd frontend && npm run lint && npm run format:check

lint-fix:
	cd backend && uv run ruff check --fix . && uv run ruff format .
	cd frontend && npm run lint:fix && npm run format

typecheck:
	cd backend && uv run mypy --config-file mypy.ini app
	cd frontend && npm run typecheck

test:
	cd backend && uv run pytest
	cd frontend && npm test

build:
	docker compose build
