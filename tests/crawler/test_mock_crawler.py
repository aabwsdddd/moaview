from __future__ import annotations

import json
import socket
from pathlib import Path

import pytest

from services.crawler.mock_crawler import MockNaverWebtoonAdapter, run_mock_crawl

FIXTURE_NAMES = ["works", "offers", "promotions", "coupons"]


def copy_fixtures(tmp_path: Path) -> Path:
    fixture_root = Path(__file__).resolve().parents[2] / "packages" / "fixtures"
    copied_root = tmp_path / "fixtures"
    copied_root.mkdir()
    for name in FIXTURE_NAMES:
        (copied_root / f"{name}.json").write_text(
            (fixture_root / f"{name}.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    return copied_root


def read_fixture(fixture_root: Path, name: str) -> list[dict[str, object]]:
    return json.loads((fixture_root / f"{name}.json").read_text(encoding="utf-8"))


def write_fixture(fixture_root: Path, name: str, rows: list[dict[str, object]]) -> None:
    (fixture_root / f"{name}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def test_mock_crawler_reads_fixture_data(tmp_path: Path) -> None:
    fixture_root = copy_fixtures(tmp_path)
    result = run_mock_crawl(fixture_root=fixture_root, state_dir=tmp_path / "state")

    assert set(result.snapshot["offers"]) == {"offer_naver_moonlight", "offer_kakao_moonlight", "offer_ridi_clockwork"}
    assert result.snapshot["offers"]["offer_kakao_moonlight"]["calculated_price"]["coupon_expected_price"] == 324
    assert all(log["adapter_name"].startswith("Mock") for log in result.crawl_logs)


def test_price_change_creates_price_history_like_record(tmp_path: Path) -> None:
    fixture_root = copy_fixtures(tmp_path)
    state_dir = tmp_path / "state"
    run_mock_crawl(fixture_root=fixture_root, state_dir=state_dir)

    offers = read_fixture(fixture_root, "offers")
    for offer in offers:
        if offer["id"] == "offer_kakao_moonlight":
            offer["base_price_krw"] = 500
            offer["last_verified_at"] = "2026-05-02T09:10:00Z"
    write_fixture(fixture_root, "offers", offers)

    result = run_mock_crawl(fixture_root=fixture_root, state_dir=state_dir)

    record = next(record for record in result.price_history if record["offer_id"] == "offer_kakao_moonlight")
    assert record["base_price"] == 500
    assert "base_price" in record["changed_fields"]
    assert set(record) >= {"offer_id", "instant_discounted_price", "coupon_expected_price", "recorded_at"}


def test_free_episode_increase_creates_notification_event_like_record(tmp_path: Path) -> None:
    fixture_root = copy_fixtures(tmp_path)
    state_dir = tmp_path / "state"
    run_mock_crawl(fixture_root=fixture_root, state_dir=state_dir)

    offers = read_fixture(fixture_root, "offers")
    for offer in offers:
        if offer["id"] == "offer_naver_moonlight":
            offer["free_episode_count"] = 8
    write_fixture(fixture_root, "offers", offers)

    result = run_mock_crawl(fixture_root=fixture_root, state_dir=state_dir)

    event = next(event for event in result.notification_events if event["event_type"] == "free_episode_count_increased")
    assert event["offer_id"] == "offer_naver_moonlight"
    assert event["payload"]["previous_free_episode_count"] == 5
    assert event["payload"]["current_free_episode_count"] == 8


def test_new_downloadable_coupon_creates_notification_event_like_record(tmp_path: Path) -> None:
    fixture_root = copy_fixtures(tmp_path)
    state_dir = tmp_path / "state"
    run_mock_crawl(fixture_root=fixture_root, state_dir=state_dir)

    coupons = read_fixture(fixture_root, "coupons")
    coupons.append(
        {
            "id": "coupon_naver_fixture_extra_30",
            "platform": "네이버웹툰",
            "coupon_type": "downloadable",
            "title": "fixture 추가 30% 쿠폰",
            "discount_type": "percent",
            "discount_value": 30,
            "downloadable": True,
            "auto_issued": False,
            "code_required": False,
            "first_purchase_only": False,
            "user_targeted": False,
            "min_purchase_amount": 100,
            "max_discount_amount": 1000,
            "starts_at": "2026-05-01T00:00:00Z",
            "ends_at": "2026-05-31T23:59:59Z",
            "requires_user_action": True,
            "label": "쿠폰 적용 예상가",
            "source_url": "https://example.com/naver/coupons/fixture-extra-30",
            "last_verified_at": "2026-05-02T09:00:00Z",
        }
    )
    write_fixture(fixture_root, "coupons", coupons)

    result = run_mock_crawl(fixture_root=fixture_root, state_dir=state_dir)

    event = next(event for event in result.notification_events if event["event_type"] == "new_downloadable_coupon")
    assert event["payload"]["coupon_ids"] == ["coupon_naver_fixture_extra_30"]


def test_failed_adapter_call_creates_crawl_log_like_record(tmp_path: Path) -> None:
    fixture_root = copy_fixtures(tmp_path)
    adapter = MockNaverWebtoonAdapter(fixture_root=fixture_root, failure_plan={"fetch_rankings": 1})

    result = run_mock_crawl(adapters=[adapter], state_dir=tmp_path / "state", max_retries=0)

    assert result.snapshot["offers"] == {}
    assert any(log["status"] == "failed" and "Simulated" in str(log["error_message"]) for log in result.crawl_logs)


def test_retry_behavior_is_deterministic(tmp_path: Path) -> None:
    fixture_root = copy_fixtures(tmp_path)
    adapter = MockNaverWebtoonAdapter(fixture_root=fixture_root, failure_plan={"fetch_rankings": 1})

    result = run_mock_crawl(adapters=[adapter], state_dir=tmp_path / "state", max_retries=1)

    retry_logs = [log for log in result.crawl_logs if log["status"] == "retrying"]
    assert len(retry_logs) == 1
    assert retry_logs[0]["notes"] == "deterministic retry 1 of 2 for fetch_rankings"
    assert set(result.snapshot["offers"]) == {"offer_naver_moonlight"}
    assert adapter.failure_plan["fetch_rankings"] == 0


def test_mock_crawl_makes_no_network_calls(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fixture_root = copy_fixtures(tmp_path)

    def fail_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("network calls are forbidden in mock crawler tests")

    monkeypatch.setattr(socket, "create_connection", fail_network)
    monkeypatch.setattr(socket.socket, "connect", fail_network)

    result = run_mock_crawl(fixture_root=fixture_root, state_dir=tmp_path / "state")

    assert len(result.snapshot["offers"]) == 3
