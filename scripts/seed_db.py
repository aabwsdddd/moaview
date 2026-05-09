"""Apply or validate the local Supabase seed file.

By default this command performs a dry run so CI can verify the seed command
without requiring a running Postgres database. Set DATABASE_URL and pass
--apply to execute the seed via psql.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = REPO_ROOT / "supabase" / "migrations"
SEED_FILE = REPO_ROOT / "supabase" / "seed.sql"


def validate_files() -> None:
    migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not migrations:
        raise SystemExit("No migration files found in supabase/migrations")
    if not SEED_FILE.exists():
        raise SystemExit("Missing supabase/seed.sql")
    for sql_file in [*migrations, SEED_FILE]:
        text = sql_file.read_text(encoding="utf-8")
        if not text.strip():
            raise SystemExit(f"{sql_file.relative_to(REPO_ROOT)} is empty")


def apply_seed(database_url: str) -> None:
    psql = shutil.which("psql")
    if psql is None:
        raise SystemExit("psql is required for --apply but was not found on PATH")
    subprocess.run(
        [psql, database_url, "-v", "ON_ERROR_STOP=1", "-f", str(SEED_FILE)],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate or apply MoaView seed data")
    parser.add_argument("--apply", action="store_true", help="Apply supabase/seed.sql using DATABASE_URL and psql")
    args = parser.parse_args()

    validate_files()
    if args.apply:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise SystemExit("DATABASE_URL is required when using --apply")
        apply_seed(database_url)
        print("Applied supabase/seed.sql")
        return

    print("Seed dry run OK: migrations and supabase/seed.sql are present")


if __name__ == "__main__":
    main()
