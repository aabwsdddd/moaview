.PHONY: check seed web api worker crawl-mock

check:
	python -m compileall services scripts
	python scripts/validate_fixtures.py
	python scripts/seed_db.py
	python -m pytest tests
	python services/crawler/run_mock_crawl.py --state-dir /tmp/moaview-crawl-state-check
	@if [ -d node_modules/@supabase/supabase-js ] && [ -d node_modules/vitest ] && [ -d node_modules/@testing-library/react ]; then npm run check && npm --workspace apps/web run test; else echo "Skipping web typecheck/tests: required node dependencies not installed"; fi

seed:
	python scripts/seed_db.py --apply

web:
	npm --workspace apps/web run dev

api:
	uvicorn services.api.app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	python -m services.worker.main


crawl-mock:
	python services/crawler/run_mock_crawl.py
