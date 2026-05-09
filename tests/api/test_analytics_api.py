from services.api.app.analytics import calculate_analytics_summary
from services.api.app.events import record_detail_view_event, record_platform_click_event, record_search_event, reset_events
from services.api.app.favorites import add_favorite_work, reset_favorites
from services.api.app.main import app
from services.api.app.routes.admin import get_analytics_summary


def setup_function() -> None:
    reset_events()
    reset_favorites()


def test_analytics_calculation_with_fixture_events() -> None:
    events = [
        {"event_type": "search", "anonymous_session_id": "anon_1", "created_at": "2026-05-01T00:00:00Z"},
        {"event_type": "search", "anonymous_session_id": "anon_2", "created_at": "2026-05-01T00:00:00Z"},
        {"event_type": "detail-view", "anonymous_session_id": "anon_1", "work_id": "work_moonlight_archive", "created_at": "2026-05-01T00:05:00Z"},
        {"event_type": "platform-click", "anonymous_session_id": "anon_1", "work_id": "work_moonlight_archive", "platform_id": "platform_kakaopage", "cta_type": "lowest_price_cta", "clicked_at": "2026-05-01T00:06:00Z"},
        {"event_type": "platform-click", "anonymous_session_id": "anon_1", "work_id": "work_moonlight_archive", "platform_id": "platform_kakaopage", "cta_type": "coupon_cta", "clicked_at": "2026-05-01T00:07:00Z"},
    ]

    summary = calculate_analytics_summary(events=events, favorites=[{"work_id": "work_moonlight_archive"}], notifications=[])

    assert summary["total_searches"] == 2
    assert summary["total_detail_views"] == 1
    assert summary["total_platform_clicks"] == 2
    assert summary["total_favorites"] == 1
    assert summary["search_to_detail_rate"] == 0.5
    assert summary["detail_to_platform_click_rate"] == 2.0
    assert summary["favorite_rate"] == 1.0
    assert summary["top_clicked_works"] == [{"work_id": "work_moonlight_archive", "title": "달빛 기록관", "count": 2}]
    assert summary["top_clicked_platforms"] == [{"platform_id": "platform_kakaopage", "label": "카카오페이지", "count": 2}]


def test_analytics_division_by_zero_does_not_crash() -> None:
    summary = calculate_analytics_summary(events=[], favorites=[], notifications=[])

    assert summary["search_to_detail_rate"] == 0.0
    assert summary["detail_to_platform_click_rate"] == 0.0
    assert summary["favorite_rate"] == 0.0
    assert summary["coupon_cta_click_rate"] == 0.0
    assert summary["notification_click_rate"] == 0.0
    assert summary["top_clicked_works"] == []


def test_coupon_cta_rate_calculation() -> None:
    events = [
        {"event_type": "detail-view", "anonymous_session_id": "anon_1", "work_id": "work_moonlight_archive", "created_at": "2026-05-01T00:05:00Z"},
        {"event_type": "detail-view", "anonymous_session_id": "anon_2", "work_id": "work_clockwork_palace", "created_at": "2026-05-01T00:05:00Z"},
        {"event_type": "platform-click", "anonymous_session_id": "anon_1", "work_id": "work_moonlight_archive", "platform_id": "platform_kakaopage", "cta_type": "coupon_cta", "clicked_at": "2026-05-01T00:07:00Z"},
    ]

    summary = calculate_analytics_summary(events=events, favorites=[], notifications=[])

    assert summary["coupon_cta_click_rate"] == 0.5
    assert summary["top_coupon_cta_works"] == [{"work_id": "work_moonlight_archive", "title": "달빛 기록관", "count": 1}]


def test_returning_user_rate_requires_elapsed_7_day_window() -> None:
    recent_events = [
        {"event_type": "search", "anonymous_session_id": "anon_recent", "created_at": "2026-05-08T00:00:00Z"},
        {"event_type": "detail-view", "anonymous_session_id": "anon_recent", "work_id": "work_moonlight_archive", "created_at": "2026-05-09T00:00:00Z"},
    ]

    recent_summary = calculate_analytics_summary(events=recent_events, generated_at="2026-05-09T00:00:00Z")

    assert recent_summary["returning_user_7_day_rate"] is None

    eligible_events = [
        {"event_type": "search", "anonymous_session_id": "anon_returning", "created_at": "2026-05-01T00:00:00Z"},
        {"event_type": "detail-view", "anonymous_session_id": "anon_returning", "work_id": "work_moonlight_archive", "created_at": "2026-05-03T00:00:00Z"},
        {"event_type": "search", "anonymous_session_id": "anon_one_time", "created_at": "2026-05-01T00:00:00Z"},
    ]

    eligible_summary = calculate_analytics_summary(events=eligible_events, generated_at="2026-05-09T00:00:00Z")

    assert eligible_summary["returning_user_7_day_rate"] == 0.5


def test_admin_analytics_summary_api_contract() -> None:
    assert any(route.path == "/api/admin/analytics/summary" and "GET" in route.methods for route in app.routes)

    record_search_event({"anonymous_session_id": "anon_1", "query": "달빛", "result_count": 1})
    record_detail_view_event({"anonymous_session_id": "anon_1", "work_id": "work_moonlight_archive"})
    record_platform_click_event({"anonymous_session_id": "anon_1", "work_id": "work_moonlight_archive", "offer_id": "offer_kakao_moonlight", "cta_type": "coupon_cta"})
    add_favorite_work("work_moonlight_archive")

    body = get_analytics_summary()
    assert body["total_searches"] == 1
    assert body["total_detail_views"] == 1
    assert body["total_platform_clicks"] == 1
    assert body["total_favorites"] == 1
    assert body["search_to_detail_rate"] == 1.0
    assert body["detail_to_platform_click_rate"] == 1.0
    assert body["coupon_cta_click_rate"] == 1.0
    assert body["generated_at"] == "2026-05-09T00:00:00Z"
    assert body["top_clicked_works"][0]["title"] == "달빛 기록관"
