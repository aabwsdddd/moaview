.PHONY: check web api worker

check:
	python -m compileall services scripts
	python scripts/validate_fixtures.py
	python -m pytest tests
	@if [ -d node_modules ]; then npm run check; else echo "Skipping web typecheck: node_modules not installed"; fi

web:
	npm --workspace apps/web run dev

api:
	uvicorn services.api.app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	python -m services.worker.main
