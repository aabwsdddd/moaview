"""Deterministic MVP analytics summaries from fixture-backed event stores."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from services.api.app.catalog import PLATFORM_IDS, get_work
from services.api.app.events import FIXTURE_TIMESTAMP, list_events
from services.api.app.favorites import list_favorite_works
from services.api.app.notifications import list_notification_events


def analytics_summary() -> dict[str, Any]:
    """Return the admin analytics summary using in-memory fixture data."""

    events = list_events()
    favorites = list_favorite_works()["items"]
    notifications = list_notification_events()["items"]
    return calculate_analytics_summary(events=events, favorites=favorites, notifications=notifications)


def calculate_analytics_summary(
    *,
    events: list[dict[str, Any]],
    favorites: list[dict[str, Any]] | None = None,
    notifications: list[dict[str, Any]] | None = None,
    generated_at: str = FIXTURE_TIMESTAMP,
) -> dict[str, Any]:
    """Calculate KPI rates and top lists from supplied fixture-compatible records."""

    favorites = favorites or []
    notifications = notifications or []
    searches = [event for event in events if event.get("event_type") == "search"]
    detail_views = [event for event in events if event.get("event_type") == "detail-view"]
    platform_clicks = [event for event in events if event.get("event_type") == "platform-click"]
    coupon_clicks = [event for event in platform_clicks if event.get("cta_type") == "coupon_cta"]
    notification_clicks = [event for event in platform_clicks if event.get("cta_type") == "notification_cta"]

    total_searches = len(searches)
    total_detail_views = len(detail_views)
    total_platform_clicks = len(platform_clicks)
    total_favorites = len(favorites)

    return {
        "total_searches": total_searches,
        "total_detail_views": total_detail_views,
        "total_platform_clicks": total_platform_clicks,
        "total_favorites": total_favorites,
        "search_to_detail_rate": _rate(total_detail_views, total_searches),
        "detail_to_platform_click_rate": _rate(total_platform_clicks, total_detail_views),
        "favorite_rate": _rate(total_favorites, total_detail_views),
        "coupon_cta_click_rate": _rate(len(coupon_clicks), total_detail_views),
        "notification_click_rate": _rate(len(notification_clicks), len(notifications)),
        "returning_user_7_day_rate": _returning_user_7_day_rate(events, generated_at=generated_at),
        "top_clicked_works": _top_works(platform_clicks),
        "top_clicked_platforms": _top_platforms(platform_clicks),
        "top_coupon_cta_works": _top_works(coupon_clicks),
        "generated_at": generated_at,
    }


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def _top_works(events: list[dict[str, Any]], *, limit: int = 5) -> list[dict[str, Any]]:
    counts = Counter(str(event.get("work_id")) for event in events if event.get("work_id"))
    items: list[dict[str, Any]] = []
    for work_id, count in counts.most_common(limit):
        work = get_work(work_id)
        items.append(
            {
                "work_id": work_id,
                "title": work["title"] if work is not None else work_id,
                "count": count,
            }
        )
    return items


def _top_platforms(events: list[dict[str, Any]], *, limit: int = 5) -> list[dict[str, Any]]:
    counts = Counter(str(event.get("platform_id")) for event in events if event.get("platform_id"))
    labels: dict[str, str] = {}
    for event in events:
        platform_id = event.get("platform_id")
        if platform_id and platform_id not in labels:
            labels[str(platform_id)] = _platform_label(str(platform_id))
    return [
        {"platform_id": platform_id, "label": labels.get(platform_id, platform_id), "count": count}
        for platform_id, count in counts.most_common(limit)
    ]


def _platform_label(platform_id: str) -> str:
    labels = {stable_id: label for label, stable_id in PLATFORM_IDS.items()}
    return labels.get(platform_id, platform_id)


def _returning_user_7_day_rate(events: list[dict[str, Any]], *, generated_at: str) -> float | None:
    """Return cohort-based repeat rate only when a 7-day window has elapsed."""

    generated_datetime = _parse_timestamp(generated_at)
    timestamps_by_identity: dict[str, list[datetime]] = defaultdict(list)
    for event in events:
        identity = event.get("user_id") or event.get("anonymous_session_id")
        timestamp = event.get("created_at") or event.get("clicked_at")
        if not identity or not timestamp:
            continue
        timestamps_by_identity[str(identity)].append(_parse_timestamp(str(timestamp)))

    eligible_identities = []
    for timestamps in timestamps_by_identity.values():
        ordered_timestamps = sorted(timestamps)
        if ordered_timestamps and generated_datetime - ordered_timestamps[0] >= timedelta(days=7):
            eligible_identities.append(ordered_timestamps)

    if not eligible_identities:
        return None

    returning = sum(1 for timestamps in eligible_identities if _has_return_within_7_days(timestamps))
    return _rate(returning, len(eligible_identities))


def _has_return_within_7_days(timestamps: list[datetime]) -> bool:
    first = timestamps[0]
    for later in timestamps[1:]:
        delta = later - first
        if timedelta(days=1) <= delta <= timedelta(days=7):
            return True
    return False


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
