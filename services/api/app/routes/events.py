"""Analytics event routes for the fixture-backed MVP."""

from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, HTTPException

from services.api.app.events import (
    EventOfferNotFoundError,
    EventWorkNotFoundError,
    MissingEventIdentityError,
    record_detail_view_event as store_detail_view_event,
    record_platform_click_event as store_platform_click_event,
    record_search_event as store_search_event,
)

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("/search")
def record_search_event(payload: dict[str, Any]) -> dict[str, object]:
    """Record a search event with a user id or anonymous session id."""

    return _record_event(store_search_event, payload)


@router.post("/detail-view")
def record_detail_view_event(payload: dict[str, Any]) -> dict[str, object]:
    """Record a work detail view event."""

    return _record_event(store_detail_view_event, payload)


@router.post("/platform-click")
def record_platform_click_event(payload: dict[str, Any]) -> dict[str, object]:
    """Record an external platform click with price and destination context."""

    return _record_event(store_platform_click_event, payload)


def _record_event(recorder: Callable[[dict[str, Any]], dict[str, object]], payload: dict[str, Any]) -> dict[str, object]:
    try:
        return recorder(payload)
    except MissingEventIdentityError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except EventWorkNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except EventOfferNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
