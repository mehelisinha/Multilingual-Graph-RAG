.PHONY: dev test build

dev:
	@echo "Starting development stack — implement in Phase 1"

test:
	cd backend && pytest
	cd frontend && npm test

build:
	docker compose build
