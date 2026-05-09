from __future__ import annotations

import json
import logging
from pathlib import Path

from services.crawler.mock_crawler import snapshot_for_fixtures
from services.worker.send_notifications import EmailPayload, render_email_payload, run_notification_worker


class RecordingProvider:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.payloads: list[EmailPayload] = []

    def send(self, payload: EmailPayload) -> str:
        self.payloads.append(payload)
        if self.fail:
            raise RuntimeError("simulated send failure")
        return "test_message_id"


def write_state(state_dir: Path, events: list[dict[str, object]]) -> dict[str, object]:
    state_dir.mkdir()
    snapshot = snapshot_for_fixtures()
    (state_dir / "snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
    (state_dir / "notification_events.json").write_text(json.dumps(events, ensure_ascii=False), encoding="utf-8")
    return snapshot


def read_events(state_dir: Path) -> list[dict[str, object]]:
    return json.loads((state_dir / "notification_events.json").read_text(encoding="utf-8"))


def notification_event(**overrides: object) -> dict[str, object]:
    event = {
        "id": "event_coupon_1",
        "notification_rule_id": None,
        "user_id": "user_1",
        "work_id": "work_moonlight_archive",
        "offer_id": "offer_kakao_moonlight",
        "event_type": "new_downloadable_coupon",
        "payload": {"platform": "카카오페이지"},
        "email_to": "reader@example.com",
        "provider_message_id": None,
        "created_at": "2026-05-09T00:00:00Z",
    }
    event.update(overrides)
    return event


def test_dry_run_email_rendering_marks_event(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    write_state(state_dir, [notification_event()])

    result = run_notification_worker(state_dir=state_dir, dry_run=True, web_base_url="https://moaview.example")
    events = read_events(state_dir)

    assert result == {"sent": 0, "dry_run_sent": 1, "skipped": 0, "failed": 0}
    assert events[0]["provider_message_id"].startswith("dry_run:")
    assert events[0]["payload"]["notification_status"] == "dry_run_sent"


def test_coupon_notification_email_includes_expected_price_label(tmp_path: Path) -> None:
    snapshot = write_state(tmp_path / "state", [notification_event()])

    payload = render_email_payload([notification_event()], snapshot=snapshot, web_base_url="https://moaview.example")

    assert payload.subject == "[MoaView] 찜한 작품에 새 쿠폰이 나왔어요"
    assert "쿠폰 적용 예상가(쿠폰 다운로드/수령 필요): 324원" in payload.text
    assert "확정가(자동 할인만 반영): 360원" in payload.text


def test_cashback_email_does_not_call_cashback_a_direct_discount(tmp_path: Path) -> None:
    snapshot = write_state(tmp_path / "state", [])
    event = notification_event(
        id="event_cashback_1",
        work_id="work_clockwork_palace",
        offer_id="offer_ridi_clockwork",
        event_type="cashback_event_started",
        payload={"platform": "리디"},
    )

    payload = render_email_payload([event], snapshot=snapshot, web_base_url="https://moaview.example")

    assert "캐시백 포함 체감가(현금 할인이 아닌 추정 가치): 64원" in payload.text
    assert "현금 할인" in payload.text
    assert "직접 할인" not in payload.text


def test_duplicate_notification_is_not_sent_twice(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    duplicate = notification_event()
    write_state(state_dir, [notification_event(), duplicate])
    provider = RecordingProvider()

    result = run_notification_worker(state_dir=state_dir, dry_run=False, provider=provider)
    events = read_events(state_dir)

    assert result == {"sent": 1, "dry_run_sent": 0, "skipped": 1, "failed": 0}
    assert len(provider.payloads) == 1
    assert events[0]["provider_message_id"] == "test_message_id"
    assert events[1]["payload"]["notification_status"] == "skipped_duplicate"


def test_missing_email_is_skipped_safely(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    write_state(state_dir, [notification_event(email_to=None)])
    provider = RecordingProvider()

    result = run_notification_worker(state_dir=state_dir, dry_run=False, provider=provider)
    events = read_events(state_dir)

    assert result == {"sent": 0, "dry_run_sent": 0, "skipped": 1, "failed": 0}
    assert provider.payloads == []
    assert events[0]["payload"]["notification_status"] == "skipped_missing_email"


def test_send_failure_is_logged(tmp_path: Path, caplog) -> None:
    state_dir = tmp_path / "state"
    write_state(state_dir, [notification_event()])
    provider = RecordingProvider(fail=True)

    with caplog.at_level(logging.ERROR):
        result = run_notification_worker(state_dir=state_dir, dry_run=False, provider=provider)

    events = read_events(state_dir)
    assert result == {"sent": 0, "dry_run_sent": 0, "skipped": 0, "failed": 1}
    assert events[0]["payload"]["notification_status"] == "failed"
    assert "Failed to send notification email" in caplog.text


def test_sent_log_idempotency_skips_event_without_resending(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    write_state(state_dir, [notification_event(provider_message_id=None)])
    (state_dir / "sent_notifications.json").write_text(
        json.dumps(
            [
                {
                    "idempotency_key": "event_coupon_1",
                    "event_id": "event_coupon_1",
                    "email_to": "reader@example.com",
                    "provider_message_id": "previous_message_id",
                    "status": "sent",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    provider = RecordingProvider()

    result = run_notification_worker(state_dir=state_dir, dry_run=False, provider=provider)
    events = read_events(state_dir)

    assert result == {"sent": 0, "dry_run_sent": 0, "skipped": 1, "failed": 0}
    assert provider.payloads == []
    assert events[0]["payload"]["notification_status"] == "skipped_duplicate"


def test_work_became_free_email_has_specific_subject(tmp_path: Path) -> None:
    snapshot = write_state(tmp_path / "state", [])
    event = notification_event(event_type="work_became_free")

    payload = render_email_payload([event], snapshot=snapshot, web_base_url="https://moaview.example")

    assert payload.subject == "[MoaView] 달빛 기록관, 카카오페이지에서 무료로 볼 수 있어요"
