"""Catalog projection helpers for fixture-backed API routes."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from services.api.app.fixtures import coupons_for_platform, load_fixture, promotions_for_platform, search_works
from services.api.app.offers import list_calculated_offers

PLATFORM_IDS = {
    "네이버웹툰": "platform_naver_webtoon",
    "카카오페이지": "platform_kakaopage",
    "리디": "platform_ridi",
}


def list_search_results(query: str) -> list[dict[str, Any]]:
    """Return enriched search result cards matching the product flow."""

    return [_search_result_for_work(work) for work in search_works(query)]


def get_work(work_id: str) -> dict[str, Any] | None:
    """Return one fixture work by id, or ``None`` when unknown."""

    return next((work for work in load_fixture("works") if work["id"] == work_id), None)


def get_work_detail(work_id: str) -> dict[str, Any] | None:
    """Return a detail page projection for a fixture work."""

    work = get_work(work_id)
    if work is None:
        return None

    offers = list_calculated_offers(work_id)
    return {
        "id": work["id"],
        "title": work["title"],
        "authors": work["authors"],
        "content_type": _content_type(work),
        "genre": work.get("genre"),
        "status": work.get("status"),
        "description": work.get("description"),
        "available_platforms": [_platform_summary(offer) for offer in offers],
    }


def get_work_offers(work_id: str) -> list[dict[str, Any]] | None:
    """Return flattened offer comparison rows for one fixture work."""

    if get_work(work_id) is None:
        return None
    return [_offer_response(offer) for offer in list_calculated_offers(work_id)]


def get_offer(offer_id: str) -> dict[str, Any] | None:
    """Return one calculated offer by fixture offer id."""

    return next((offer for offer in list_calculated_offers() if offer["id"] == offer_id), None)


def platform_id_for(platform: str) -> str:
    """Return a stable fixture platform id for a display label."""

    return PLATFORM_IDS.get(platform, platform.casefold().replace(" ", "_"))


def _search_result_for_work(work: dict[str, Any]) -> dict[str, Any]:
    offers = list_calculated_offers(work["id"])
    calculated_prices = [offer["calculated_price"] for offer in offers]
    best_offer = min(
        offers,
        key=lambda offer: (offer["calculated_price"]["effective_price_for_sort"], offer["platform"]),
        default=None,
    )
    return {
        "id": work["id"],
        "title": work["title"],
        "authors": work["authors"],
        "content_type": _content_type(work),
        "platforms": [_platform_summary(offer) for offer in offers],
        "max_free_episodes": max((offer["free_episode_count"] for offer in offers), default=0),
        "lowest_confirmed_price": min(
            (price["instant_discounted_price"] for price in calculated_prices),
            default=None,
        ),
        "lowest_coupon_expected_price": min(
            (
                price["coupon_expected_price"]
                for price in calculated_prices
                if price["coupon_expected_price"] is not None
            ),
            default=None,
        ),
        "best_platform_label": best_offer["platform"] if best_offer is not None else None,
    }


def _offer_response(offer: dict[str, Any]) -> dict[str, Any]:
    calculated_price = offer["calculated_price"]
    active_promotions = _active_items(promotions_for_platform(offer["platform"]), offer["last_verified_at"])
    active_coupons = _active_items(coupons_for_platform(offer["platform"]), offer["last_verified_at"])
    return {
        "id": offer["id"],
        "work_id": offer["work_id"],
        "platform": offer["platform"],
        "platform_id": platform_id_for(offer["platform"]),
        "source_url": offer["source_url"],
        "last_updated_at": offer["last_verified_at"],
        "free_episode_count": offer["free_episode_count"],
        "wait_free_available": offer["wait_free_available"],
        "base_price": calculated_price["base_price"],
        "instant_discounted_price": calculated_price["instant_discounted_price"],
        "coupon_expected_price": calculated_price["coupon_expected_price"],
        "cashback_adjusted_price": calculated_price["cashback_adjusted_price"],
        "effective_price_for_sort": calculated_price["effective_price_for_sort"],
        "price_confidence": calculated_price["price_confidence"],
        "calculation_note": calculated_price["calculation_note"],
        "active_promotions": active_promotions,
        "active_coupons": active_coupons,
    }


def _platform_summary(offer: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": platform_id_for(offer["platform"]),
        "label": offer["platform"],
        "offer_id": offer["id"],
        "source_url": offer["source_url"],
        "last_updated_at": offer["last_verified_at"],
    }


def _active_items(items: list[dict[str, Any]], timestamp: str) -> list[dict[str, Any]]:
    now = _coerce_datetime(timestamp)
    return [dict(item) for item in items if _item_is_active(item, now)]


def _item_is_active(item: dict[str, Any], now: datetime) -> bool:
    starts_at = item.get("starts_at")
    ends_at = item.get("ends_at")
    if starts_at is not None and _coerce_datetime(starts_at) > now:
        return False
    if ends_at is not None and _coerce_datetime(ends_at) < now:
        return False
    return True


def _content_type(work: dict[str, Any]) -> str:
    return str(work.get("content_type") or work.get("type"))


def _coerce_datetime(value: datetime | str | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(timezone.utc)
