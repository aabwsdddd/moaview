.PHONY: check seed web api worker

check:
	python -m compileall services scripts
	python scripts/validate_fixtures.py
	python scripts/seed_db.py
	python -m pytest tests
	@if [ -d node_modules ]; then npm run check && npm --workspace apps/web run test; else echo "Skipping web typecheck/tests: node_modules not installed"; fi

seed:
	python scripts/seed_db.py --apply

web:
	npm --workspace apps/web run dev

api:
	uvicorn services.api.app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	python -m services.worker.main
