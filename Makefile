.PHONY: help dev test build backend-start frontend-start clean cli-install cli-setup

help:
	@echo "UIBench Makefile"
	@echo "  make dev           - Start full stack with docker-compose"
	@echo "  make backend-start - Start backend locally"
	@echo "  make frontend-start - Start frontend locally"
	@echo "  make test          - Run tests"
	@echo "  make build         - Build Docker images"
	@echo "  make clean         - Remove build artifacts"
	@echo "  make cli-install   - Install CLI-only dependencies"
	@echo "  make cli-setup     - Run interactive setup for CLI mode"

dev:
	docker compose up --build

backend-start:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-start:
	cd frontend && pnpm dev

test:
	cd backend && python -m pytest tests/ -v
	cd frontend && pnpm test:unit

build:
	docker compose build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name dist -exec rm -rf {} +
	find . -type d -name node_modules -exec rm -rf {} +

cli-install:
	pip install -e ".[cli]"
	playwright install chromium

cli-setup:
	python scripts/setup.py
