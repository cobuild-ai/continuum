.PHONY: help install test run dev lint clean

help:
	@echo "🌌 Continuum - Mobile-First Vibe Coding & Host Sandbox Orchestrator"
	@echo "Usage:"
	@echo "  make install     Install dependencies using uv"
	@echo "  make run         Run Vibe Server (FastAPI)"
	@echo "  make test        Run unit tests"
	@echo "  make lint        Check syntax & type cleanliness"
	@echo "  make clean       Clean temporary and cache files"

install:
	uv sync

run:
	uv run uvicorn vibe_server.main:app --host 0.0.0.0 --port 8080 --reload

test:
	uv run pytest tests/ -v

lint:
	python3 -m py_compile $$(find vibe_server -name "*.py") $$(find tests -name "*.py")

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
