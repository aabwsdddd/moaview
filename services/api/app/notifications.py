"""Notification projections for fixture-compatible in-memory events."""

from __future__ import annotations

from services.api.app.events import list_events


def list_notification_events() -> dict[str, object]:
    """Return fixture-compatible notification records derived from event records."""

    items = [
        {
            "id": f"notification_{event['id']}",
            "event_type": event["event_type"],
            "work_id": event.get("work_id"),
            "user_id": event.get("user_id"),
            "anonymous_session_id": event.get("anonymous_session_id"),
            "payload": event,
            "created_at": event.get("clicked_at") or event.get("created_at"),
        }
        for event in list_events()
        if event["event_type"] in {"detail-view", "platform-click"}
    ]
    return {"items": items, "count": len(items)}
