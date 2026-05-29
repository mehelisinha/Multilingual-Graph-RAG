.PHONY: dev dev-infra stop test build lint lint-fix format typecheck install-dev install-ci migrate

install-dev:
	cd backend && pip install -r requirements-dev.txt
	cd frontend && npm install

install-ci:
	cd backend && pip install -r requirements-ci.txt

migrate:
	cd backend && alembic upgrade head

dev-infra:
	docker compose up -d postgres redis neo4j etcd minio milvus

dev:
	docker compose up -d --build

stop:
	docker compose down

lint:
	cd backend && ruff check . && ruff format --check .
	cd frontend && npm run lint && npm run format:check

lint-fix:
	cd backend && ruff check --fix . && ruff format .
	cd frontend && npm run lint:fix && npm run format

typecheck:
	cd backend && mypy --config-file mypy.ini app
	cd frontend && npm run typecheck

test:
	cd backend && pytest
	cd frontend && npm test

build:
	docker compose build
