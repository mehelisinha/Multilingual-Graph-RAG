.PHONY: dev test build lint lint-fix format typecheck install-dev

install-dev:
	cd backend && pip install -r requirements-dev.txt
	cd frontend && npm install

lint:
	cd backend && ruff check . && ruff format --check .
	cd frontend && npm run lint && npm run format:check

lint-fix:
	cd backend && ruff check --fix . && ruff format .
	cd frontend && npm run lint:fix && npm run format

typecheck:
	cd backend && mypy app
	cd frontend && npm run typecheck

test:
	cd backend && pytest
	cd frontend && npm test

dev:
	@echo "Starting development stack - implement in Phase 1"

build:
	docker compose build
