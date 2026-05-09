"""Fixture offer helpers with deterministic calculated pricing."""

from __future__ import annotations

from typing import Any

from services.api.app.fixtures import coupons_for_platform, load_fixture, promotions_for_platform
from services.api.app.pricing import calculate_offer_price


def list_calculated_offers(work_id: str | None = None) -> list[dict[str, Any]]:
    """Return fixture offers enriched with deterministic calculated prices."""

    offers = load_fixture("offers")
    if work_id is not None:
        offers = [offer for offer in offers if offer["work_id"] == work_id]

    enriched_offers = []
    for offer in offers:
        enriched_offer = dict(offer)
        enriched_offer["calculated_price"] = calculate_offer_price(
            paid_episode_price=offer["base_price_krw"],
            currency_type="KRW",
            free_episode_count=offer["free_episode_count"],
            wait_free_available=offer["wait_free_available"],
            promotions=promotions_for_platform(offer["platform"]),
            coupons=coupons_for_platform(offer["platform"]),
            current_timestamp=offer["last_verified_at"],
        )
        enriched_offers.append(enriched_offer)
    return enriched_offers
