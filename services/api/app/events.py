"""In-memory analytics event store for the fixture-backed API MVP."""

from __future__ import annotations

from typing import Any

from services.api.app.catalog import get_offer, get_work, platform_id_for

FIXTURE_TIMESTAMP = "2026-05-09T00:00:00Z"

_EVENTS: dict[str, list[dict[str, Any]]] = {
    "search": [],
    "detail-view": [],
    "platform-click": [],
}


class MissingEventIdentityError(ValueError):
    """Raised when an event lacks both user and anonymous session identity."""


class EventWorkNotFoundError(ValueError):
    """Raised when an event references an unknown fixture work."""


class EventOfferNotFoundError(ValueError):
    """Raised when a click event references an unknown offer for the work."""


def reset_events() -> None:
    """Clear in-memory event lists for deterministic tests."""

    for events in _EVENTS.values():
        events.clear()


def list_events(event_type: str | None = None) -> list[dict[str, Any]]:
    """Return stored in-memory events for tests and notification projections."""

    if event_type is not None:
        return list(_EVENTS[event_type])
    return [event for events in _EVENTS.values() for event in events]


def record_search_event(payload: dict[str, Any]) -> dict[str, object]:
    """Record a search event with a user id or anonymous session id."""

    _require_identity(payload)
    query = str(payload.get("query") or payload.get("q") or "")
    event = {
        "id": _next_id("search"),
        "event_type": "search",
        "user_id": payload.get("user_id"),
        "anonymous_session_id": payload.get("anonymous_session_id"),
        "query": query,
        "result_count": int(payload.get("result_count", 0)),
        "created_at": str(payload.get("created_at") or FIXTURE_TIMESTAMP),
    }
    _EVENTS["search"].append(event)
    return {"item": event, "count": len(_EVENTS["search"])}


def record_detail_view_event(payload: dict[str, Any]) -> dict[str, object]:
    """Record a work detail view event."""

    _require_identity(payload)
    work_id = str(payload.get("work_id", ""))
    if get_work(work_id) is None:
        raise EventWorkNotFoundError("Work not found")
    event = {
        "id": _next_id("detail-view"),
        "event_type": "detail-view",
        "user_id": payload.get("user_id"),
        "anonymous_session_id": payload.get("anonymous_session_id"),
        "work_id": work_id,
        "created_at": str(payload.get("created_at") or FIXTURE_TIMESTAMP),
    }
    _EVENTS["detail-view"].append(event)
    return {"item": event, "count": len(_EVENTS["detail-view"])}


def record_platform_click_event(payload: dict[str, Any]) -> dict[str, object]:
    """Record an external platform click with price and destination context."""

    _require_identity(payload)
    work_id = str(payload.get("work_id", ""))
    offer_id = str(payload.get("offer_id", ""))
    offer = get_offer(offer_id)
    if get_work(work_id) is None:
        raise EventWorkNotFoundError("Work not found")
    if offer is None or offer["work_id"] != work_id:
        raise EventOfferNotFoundError("Offer not found for work")

    effective_price = payload.get("effective_price_at_click")
    if effective_price is None:
        effective_price = offer["calculated_price"]["effective_price_for_sort"]
    event = {
        "id": _next_id("platform-click"),
        "event_type": "platform-click",
        "user_id": payload.get("user_id"),
        "anonymous_session_id": payload.get("anonymous_session_id"),
        "work_id": work_id,
        "platform_id": str(payload.get("platform_id") or platform_id_for(offer["platform"])),
        "offer_id": offer_id,
        "cta_type": str(payload.get("cta_type") or "open_platform"),
        "effective_price_at_click": int(effective_price),
        "destination_url": str(payload.get("destination_url") or offer["source_url"]),
        "clicked_at": str(payload.get("clicked_at") or FIXTURE_TIMESTAMP),
    }
    _EVENTS["platform-click"].append(event)
    return {"item": event, "count": len(_EVENTS["platform-click"])}


def _require_identity(payload: dict[str, Any]) -> None:
    if payload.get("user_id") or payload.get("anonymous_session_id"):
        return
    raise MissingEventIdentityError("anonymous_session_id is required when user_id is not available")


def _next_id(event_type: str) -> str:
    return f"event_{event_type}_{len(_EVENTS[event_type]) + 1}"
