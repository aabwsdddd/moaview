"""Mock crawler adapter that returns local fixture snapshots only."""

from __future__ import annotations

from services.api.app.fixtures import load_fixture


class MockCrawler:
    """Fixture-backed crawler replacement for MVP development."""

    def fetch_offers(self, work_id: str | None = None) -> list[dict[str, object]]:
        """Return fixture offers without network scraping."""

        offers = load_fixture("offers")
        if work_id is None:
            return offers
        return [offer for offer in offers if offer["work_id"] == work_id]
