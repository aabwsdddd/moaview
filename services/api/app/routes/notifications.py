"""Fixture-compatible notification event routes."""

from __future__ import annotations

from fastapi import APIRouter

from services.api.app.notifications import list_notification_events

router = APIRouter(prefix="/api", tags=["notifications"])


@router.get("/notifications")
def list_notifications() -> dict[str, object]:
    """Return fixture-compatible notification records derived from events for now."""

    return list_notification_events()
