import pytest

from services.api.app.events import (
    MissingEventIdentityError,
    record_detail_view_event,
    record_platform_click_event,
    record_search_event,
    reset_events,
)
from services.api.app.notifications import list_notification_events


def setup_function() -> None:
    reset_events()


def test_events_require_anonymous_session_when_user_is_missing() -> None:
    with pytest.raises(MissingEventIdentityError) as exc_info:
        record_search_event({"query": "달빛"})

    assert "anonymous_session_id" in str(exc_info.value)


def test_records_search_and_detail_view_events() -> None:
    search_body = record_search_event({"anonymous_session_id": "anon_1", "query": "달빛", "result_count": 1})
    detail_body = record_detail_view_event({"anonymous_session_id": "anon_1", "work_id": "work_moonlight_archive"})

    assert search_body["item"]["query"] == "달빛"
    assert detail_body["item"]["work_id"] == "work_moonlight_archive"


def test_platform_click_event_stores_required_click_context() -> None:
    body = record_platform_click_event(
        {
            "anonymous_session_id": "anon_1",
            "work_id": "work_moonlight_archive",
            "platform_id": "platform_kakaopage",
            "offer_id": "offer_kakao_moonlight",
            "cta_type": "compare_cta",
            "effective_price_at_click": 324,
            "destination_url": "https://example.com/kakao/moonlight-archive",
            "clicked_at": "2026-05-09T12:00:00Z",
        }
    )

    event = body["item"]
    assert event["work_id"] == "work_moonlight_archive"
    assert event["platform_id"] == "platform_kakaopage"
    assert event["offer_id"] == "offer_kakao_moonlight"
    assert event["cta_type"] == "compare_cta"
    assert event["effective_price_at_click"] == 324
    assert event["destination_url"] == "https://example.com/kakao/moonlight-archive"
    assert event["clicked_at"] == "2026-05-09T12:00:00Z"


def test_notifications_project_notification_records_from_events() -> None:
    record_platform_click_event(
        {
            "anonymous_session_id": "anon_1",
            "work_id": "work_moonlight_archive",
            "offer_id": "offer_kakao_moonlight",
        }
    )

    body = list_notification_events()

    assert body["count"] == 1
    assert body["items"][0]["event_type"] == "platform-click"
