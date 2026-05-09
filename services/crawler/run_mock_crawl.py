"""CLI entry point for the fixture-only mock crawler."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.crawler.mock_crawler import DEFAULT_STATE_DIR, run_mock_crawl


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the MoaView fixture-only mock crawler")
    parser.add_argument(
        "--state-dir",
        type=Path,
        default=DEFAULT_STATE_DIR,
        help="Directory for local JSON crawl state (default: .local/crawl-state)",
    )
    parser.add_argument("--max-retries", type=int, default=2, help="Deterministic retry count for simulated failures")
    args = parser.parse_args()

    result = run_mock_crawl(state_dir=args.state_dir, max_retries=args.max_retries)
    print(f"Mock crawl complete: {len(result.snapshot['offers'])} offers")
    print(f"Price history records: {len(result.price_history)}")
    print(f"Notification events: {len(result.notification_events)}")
    print(f"Crawl logs: {len(result.crawl_logs)}")
    print(f"State directory: {args.state_dir}")


if __name__ == "__main__":
    main()
