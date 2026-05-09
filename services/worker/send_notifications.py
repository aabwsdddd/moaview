"""Email notification worker for mock-crawler notification events.

The MVP worker reads fixture-compatible notification events from the local mock
crawler state directory, renders Korean email copy, and either sends through
Resend or writes dry-run delivery records. Tests and local development never
need real Resend credentials when ``NOTIFICATION_DRY_RUN=true`` (the default).
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import logging
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.api.app.fixtures import load_fixture
from services.crawler.mock_crawler import DEFAULT_STATE_DIR

LOGGER = logging.getLogger("moaview.worker.notifications")
DEFAULT_FROM_EMAIL = "MoaView <notifications@moaview.local>"
DELIVERED_STATUSES = {"sent", "dry_run_sent"}

EVENT_LABELS = {
    "free_episode_count_increased": "무료 회차 증가",
    "work_became_free": "무료 전환",
    "wait_free_availability_changed": "기다리면 무료 변경",
    "instant_discount_promotion_started": "즉시 할인 시작",
    "new_promotion_started": "프로모션 시작",
    "new_downloadable_coupon": "다운로드 쿠폰 등장",
    "coupon_expected_price_decreased": "쿠폰 적용 예상가 하락",
    "cashback_event_started": "캐시백 이벤트 시작",
}


@dataclass(frozen=True)
class EmailPayload:
    """Rendered email payload ready for dry-run logging or Resend."""

    to: str
    subject: str
    html: str
    text: str
    event_ids: list[str]


class EmailProvider(Protocol):
    """Provider interface used by tests and the Resend implementation."""

    def send(self, payload: EmailPayload) -> str:
        """Send one payload and return a provider message id."""


class DryRunEmailProvider:
    """Email provider that logs payloads instead of sending network requests."""

    def send(self, payload: EmailPayload) -> str:
        LOGGER.info(
            "Dry-run email payload: to=%s subject=%s event_ids=%s text=%s",
            payload.to,
            payload.subject,
            ",".join(payload.event_ids),
            payload.text,
        )
        digest = hashlib.sha256("|".join(payload.event_ids).encode("utf-8")).hexdigest()[:16]
        return f"dry_run:{digest}"


class ResendEmailProvider:
    """Minimal Resend REST client using the standard library."""

    def __init__(self, *, api_key: str, from_email: str = DEFAULT_FROM_EMAIL) -> None:
        if not api_key:
            raise ValueError("RESEND_API_KEY is required when NOTIFICATION_DRY_RUN is false")
        self.api_key = api_key
        self.from_email = from_email

    def send(self, payload: EmailPayload) -> str:
        request_body = json.dumps(
            {
                "from": self.from_email,
                "to": [payload.to],
                "subject": payload.subject,
                "html": payload.html,
                "text": payload.text,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            "https://api.resend.com/emails",
            data=request_body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:  # noqa: S310 - fixed Resend API URL.
                response_payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:  # pragma: no cover - network path is not used in tests.
            raise RuntimeError(f"Resend request failed: {exc}") from exc
        return str(response_payload.get("id") or response_payload.get("message_id") or "resend:unknown")


def main() -> None:
    parser = argparse.ArgumentParser(description="Send or dry-run MoaView notification emails")
    parser.add_argument(
        "--state-dir",
        type=Path,
        default=DEFAULT_STATE_DIR,
        help="Directory containing mock crawler notification_events.json and snapshot.json",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    result = run_notification_worker(state_dir=args.state_dir)
    print(
        "Notification worker complete: "
        f"sent={result['sent']} dry_run_sent={result['dry_run_sent']} "
        f"skipped={result['skipped']} failed={result['failed']}"
    )


def run_notification_worker(
    *,
    state_dir: Path = DEFAULT_STATE_DIR,
    dry_run: bool | None = None,
    web_base_url: str | None = None,
    provider: EmailProvider | None = None,
) -> dict[str, int]:
    """Process pending notification events from local crawler state."""

    effective_dry_run = _env_bool("NOTIFICATION_DRY_RUN", default=True) if dry_run is None else dry_run
    effective_web_base_url = (web_base_url or os.environ.get("MOAVIEW_WEB_BASE_URL") or "http://localhost:3000").rstrip("/")
    email_provider = provider or (
        DryRunEmailProvider()
        if effective_dry_run
        else ResendEmailProvider(api_key=os.environ.get("RESEND_API_KEY", ""), from_email=os.environ.get("RESEND_FROM_EMAIL", DEFAULT_FROM_EMAIL))
    )

    notification_path = state_dir / "notification_events.json"
    events = _read_json_list(notification_path)
    if not events:
        LOGGER.info("No notification events found at %s", notification_path)
        return {"sent": 0, "dry_run_sent": 0, "skipped": 0, "failed": 0}

    snapshot = _read_json_dict(state_dir / "snapshot.json")
    sent_log_path = state_dir / "sent_notifications.json"
    sent_log = _read_json_list(sent_log_path)
    sent_keys = {str(record.get("idempotency_key")) for record in sent_log if record.get("idempotency_key")}

    pending: list[dict[str, Any]] = []
    counts = {"sent": 0, "dry_run_sent": 0, "skipped": 0, "failed": 0}
    for event in events:
        if _is_delivered(event):
            continue
        if _idempotency_key(event) in sent_keys:
            _mark_event(event, status="skipped_duplicate", error_message="idempotency key was already delivered")
            counts["skipped"] += 1
            continue
        pending.append(event)

    grouped = group_events_by_email(pending)
    processed_keys: set[str] = set()

    for event in pending:
        if not _event_email(event):
            _mark_event(event, status="skipped_missing_email", error_message="email_to is missing")
            LOGGER.warning("Skipping notification %s because email_to is missing", event.get("id"))
            counts["skipped"] += 1

    for email, email_events in grouped.items():
        unique_events = []
        for event in email_events:
            key = _idempotency_key(event)
            if key in processed_keys:
                _mark_event(event, status="skipped_duplicate", error_message="duplicate notification id")
                LOGGER.info("Skipping duplicate notification %s", event.get("id"))
                counts["skipped"] += 1
                continue
            processed_keys.add(key)
            unique_events.append(event)
        if not unique_events:
            continue

        try:
            payload = render_email_payload(unique_events, snapshot=snapshot, web_base_url=effective_web_base_url)
            message_id = email_provider.send(payload)
            status = "dry_run_sent" if effective_dry_run or message_id.startswith("dry_run:") else "sent"
            for event in unique_events:
                _mark_event(event, status=status, provider_message_id=message_id)
                sent_log.append(
                    {
                        "idempotency_key": _idempotency_key(event),
                        "event_id": event.get("id"),
                        "email_to": email,
                        "provider_message_id": message_id,
                        "status": status,
                    }
                )
            counts[status] += len(unique_events)
        except Exception as exc:  # noqa: BLE001 - one bad email must not stop the batch.
            LOGGER.exception("Failed to send notification email to %s", email)
            for event in unique_events:
                _mark_event(event, status="failed", error_message=str(exc))
            counts["failed"] += len(unique_events)

    _write_json(notification_path, events)
    _write_json(sent_log_path, sent_log)
    return counts


def group_events_by_email(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group events by email address when user/email data exists."""

    grouped: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        email = _event_email(event)
        if not email:
            continue
        grouped.setdefault(email, []).append(event)
    return grouped


def render_email_payload(events: list[dict[str, Any]], *, snapshot: dict[str, Any], web_base_url: str) -> EmailPayload:
    """Render Korean subject plus HTML/text bodies for one recipient."""

    if not events:
        raise ValueError("At least one event is required to render an email")
    recipient = _event_email(events[0])
    if recipient is None:
        raise ValueError("email_to is required to render an email")

    rendered_items = [_render_event_item(event, snapshot=snapshot, web_base_url=web_base_url) for event in events]
    subject = _subject_for(rendered_items)
    text_lines = [subject, ""]
    html_items = []
    for item in rendered_items:
        text_lines.extend(item["text_lines"])
        text_lines.append("")
        html_items.append(item["html"])
    html_body = (
        "<html><body>"
        "<h1>MoaView 알림</h1>"
        "<p>찜한 작품의 가격/혜택 변동을 확인해 보세요.</p>"
        + "".join(html_items)
        + "</body></html>"
    )
    return EmailPayload(
        to=recipient,
        subject=subject,
        html=html_body,
        text="\n".join(text_lines).strip(),
        event_ids=[str(event.get("id")) for event in events],
    )


def _render_event_item(event: dict[str, Any], *, snapshot: dict[str, Any], web_base_url: str) -> dict[str, Any]:
    offer_entry = (snapshot.get("offers") or {}).get(event.get("offer_id"), {})
    offer = offer_entry.get("offer") or {}
    calculated_price = offer_entry.get("calculated_price") or {}
    work = _work_by_id(str(event.get("work_id") or offer.get("work_id") or ""))

    title = str(work.get("title") or event.get("work_id") or "알 수 없는 작품")
    platform = str((event.get("payload") or {}).get("platform") or offer.get("platform") or "알 수 없는 플랫폼")
    source_url = str(offer.get("source_url") or (event.get("payload") or {}).get("source_url") or "")
    last_verified_at = str(offer.get("last_verified_at") or (event.get("payload") or {}).get("last_verified_at") or event.get("created_at") or "")
    cta_url = f"{web_base_url}/works/{event.get('work_id') or offer.get('work_id')}"
    event_label = EVENT_LABELS.get(str(event.get("event_type")), str(event.get("event_type")))

    price_lines = _price_lines(calculated_price)
    text_lines = [
        f"작품: {title}",
        f"플랫폼: {platform}",
        f"알림 유형: {event_label}",
        *price_lines,
        f"출처: {source_url}" if source_url else "출처: 미확인",
        f"마지막 확인: {last_verified_at}" if last_verified_at else "마지막 확인: 미확인",
        f"바로 보기: {cta_url}",
    ]
    html_rows = "".join(f"<li>{html.escape(line)}</li>" for line in text_lines[2:])
    html_body = (
        "<section style=\"margin:16px 0;padding:16px;border:1px solid #ddd;border-radius:8px\">"
        f"<h2>{html.escape(title)} · {html.escape(platform)}</h2>"
        f"<ul>{html_rows}</ul>"
        f"<p><a href=\"{html.escape(cta_url, quote=True)}\">MoaView에서 비교하기</a></p>"
        "</section>"
    )
    return {
        "title": title,
        "platform": platform,
        "event_type": str(event.get("event_type")),
        "event_label": event_label,
        "html": html_body,
        "text_lines": text_lines,
    }


def _price_lines(calculated_price: dict[str, Any]) -> list[str]:
    lines = [
        f"기준 가격: {_format_krw(calculated_price.get('base_price'))}",
        f"확정가(자동 할인만 반영): {_format_krw(calculated_price.get('instant_discounted_price'))}",
    ]
    if calculated_price.get("coupon_expected_price") is not None:
        lines.append(f"쿠폰 적용 예상가(쿠폰 다운로드/수령 필요): {_format_krw(calculated_price.get('coupon_expected_price'))}")
    if calculated_price.get("cashback_adjusted_price") is not None:
        lines.append(
            f"캐시백 포함 체감가(현금 할인이 아닌 추정 가치): {_format_krw(calculated_price.get('cashback_adjusted_price'))}"
        )
    return lines


def _subject_for(items: list[dict[str, Any]]) -> str:
    if len(items) > 1:
        return f"[MoaView] 찜한 작품에 새 알림 {len(items)}건이 있어요"
    item = items[0]
    if item["event_type"] == "new_downloadable_coupon":
        return "[MoaView] 찜한 작품에 새 쿠폰이 나왔어요"
    if item["event_type"] == "coupon_expected_price_decreased":
        return f"[MoaView] {item['title']}, {item['platform']}에서 쿠폰 적용 예상가가 내려갔어요"
    if item["event_type"] == "free_episode_count_increased":
        return "[MoaView] 무료 회차가 증가했어요"
    if item["event_type"] == "work_became_free":
        return f"[MoaView] {item['title']}, {item['platform']}에서 무료로 볼 수 있어요"
    if item["event_type"] == "cashback_event_started":
        return f"[MoaView] {item['title']}, {item['platform']}에서 캐시백 이벤트가 시작됐어요"
    if item["event_type"] == "instant_discount_promotion_started":
        return f"[MoaView] {item['title']}, {item['platform']}에서 즉시 할인이 시작됐어요"
    return f"[MoaView] {item['title']} 혜택 알림이 도착했어요"


def _work_by_id(work_id: str) -> dict[str, Any]:
    for work in load_fixture("works"):
        if work.get("id") == work_id:
            return work
    return {}


def _is_delivered(event: dict[str, Any]) -> bool:
    payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
    return bool(event.get("provider_message_id")) or payload.get("notification_status") in DELIVERED_STATUSES


def _mark_event(
    event: dict[str, Any], *, status: str, provider_message_id: str | None = None, error_message: str | None = None
) -> None:
    payload = event.setdefault("payload", {})
    if not isinstance(payload, dict):
        payload = {}
        event["payload"] = payload
    payload["notification_status"] = status
    if error_message:
        payload["notification_error"] = error_message
    if provider_message_id:
        event["provider_message_id"] = provider_message_id


def _idempotency_key(event: dict[str, Any]) -> str:
    if event.get("id"):
        return str(event["id"])
    raw = "|".join(str(event.get(field, "")) for field in ["event_type", "user_id", "email_to", "work_id", "offer_id", "created_at"])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _event_email(event: dict[str, Any]) -> str | None:
    email = event.get("email_to") or (event.get("payload") or {}).get("email_to")
    if not email:
        return None
    return str(email).strip().lower() or None


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as input_file:
        data = json.load(input_file)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return data


def _read_json_dict(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as input_file:
        data = json.load(input_file)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output_file:
        json.dump(payload, output_file, ensure_ascii=False, indent=2, sort_keys=True)
        output_file.write("\n")


def _format_krw(value: Any) -> str:
    if value is None:
        return "미확인"
    return f"{int(value):,}원"


def _env_bool(name: str, *, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


if __name__ == "__main__":
    main()
