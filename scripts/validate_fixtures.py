from __future__ import annotations

import json
from pathlib import Path

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "packages" / "fixtures"
REQUIRED_OFFER_FIELDS = {
    "base_price_krw",
    "instant_discount_krw",
    "coupon_expected_discount_krw",
    "cashback_rate",
    "free_episode_count",
    "wait_free_available",
    "source_url",
    "last_verified_at",
}


def load(name: str) -> list[dict[str, object]]:
    with (FIXTURE_ROOT / f"{name}.json").open(encoding="utf-8") as fixture_file:
        data = json.load(fixture_file)
    if not isinstance(data, list):
        raise AssertionError(f"{name}.json must contain an array")
    return data


def main() -> None:
    for name in ["works", "offers", "promotions", "coupons"]:
        load(name)

    for offer in load("offers"):
        missing = REQUIRED_OFFER_FIELDS - offer.keys()
        if missing:
            raise AssertionError(f"Offer {offer.get('id')} missing fields: {sorted(missing)}")


if __name__ == "__main__":
    main()
