"""Fixture-only crawler adapters and deterministic change detection.

This module intentionally never performs network I/O.  The adapters read local
JSON fixtures, calculate offer prices with the existing pricing module, and
persist mock crawl snapshots under ``.local/crawl-state`` by default.
"""

from __future__ import annotations

import json
import os
import uuid
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

from services.api.app.fixtures import FIXTURE_ROOT, load_fixture, search_works
from services.api.app.pricing import calculate_offer_price

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATE_DIR = REPO_ROOT / ".local" / "crawl-state"
PLATFORM_SLUGS = {
    "네이버웹툰": "naver-webtoon",
    "카카오페이지": "kakaopage",
    "리디": "ridi",
}
PLATFORM_ADAPTERS = {
    "네이버웹툰": "MockNaverWebtoonAdapter",
    "카카오페이지": "MockKakaoPageAdapter",
    "리디": "MockRidiAdapter",
}


class AdapterError(RuntimeError):
    """Raised for deterministic, simulated adapter failures."""


class PlatformAdapter(ABC):
    """Interface for platform adapters.

    MVP implementations must use local fixtures only.  Production scraping,
    platform login, authenticated pages, anti-bot bypassing, and external
    platform calls are deliberately out of scope.
    """

    platform: str
    adapter_name: str

    @abstractmethod
    def search_works(self, query: str) -> list[dict[str, Any]]:
        """Return works from local fixtures that match ``query``."""

    @abstractmethod
    def fetch_work_detail(self, platform_work_id: str) -> dict[str, Any]:
        """Return one fixture work by local work/platform-work identifier."""

    @abstractmethod
    def fetch_offers(self, platform_work_id: str | None = None) -> list[dict[str, Any]]:
        """Return fixture offers for this adapter's platform."""

    @abstractmethod
    def fetch_promotions(self, platform_work_id: str | None = None) -> list[dict[str, Any]]:
        """Return fixture promotions for this adapter's platform."""

    @abstractmethod
    def fetch_coupons(self, platform_work_id: str | None = None) -> list[dict[str, Any]]:
        """Return fixture coupons for this adapter's platform."""

    @abstractmethod
    def fetch_rankings(self) -> list[dict[str, Any]]:
        """Return deterministic fixture rankings for this adapter's platform."""


class FixturePlatformAdapter(PlatformAdapter):
    """Base class for adapters backed only by local fixture JSON files."""

    platform = ""
    adapter_name = "FixturePlatformAdapter"

    def __init__(
        self,
        *,
        fixture_root: Path | None = None,
        failure_plan: dict[str, int] | None = None,
    ) -> None:
        self.fixture_root = fixture_root or FIXTURE_ROOT
        self.failure_plan = dict(failure_plan or {})

    def search_works(self, query: str) -> list[dict[str, Any]]:
        self._maybe_fail("search_works")
        platform_work_ids = {offer["work_id"] for offer in self.fetch_offers(None)}
        return [work for work in self._search_works(query) if work["id"] in platform_work_ids]

    def fetch_work_detail(self, platform_work_id: str) -> dict[str, Any]:
        self._maybe_fail("fetch_work_detail")
        work_id = self._normalize_platform_work_id(platform_work_id)
        for work in self._load_fixture("works"):
            if work["id"] == work_id:
                detail = dict(work)
                detail["platform"] = self.platform
                detail["platform_work_id"] = self._platform_work_id(work_id)
                return detail
        raise KeyError(f"Unknown fixture work for {self.adapter_name}: {platform_work_id}")

    def fetch_offers(self, platform_work_id: str | None = None) -> list[dict[str, Any]]:
        self._maybe_fail("fetch_offers")
        work_id = self._normalize_platform_work_id(platform_work_id) if platform_work_id else None
        offers = [offer for offer in self._load_fixture("offers") if offer["platform"] == self.platform]
        if work_id is not None:
            offers = [offer for offer in offers if offer["work_id"] == work_id]
        return [self._with_platform_work_id(offer) for offer in offers]

    def fetch_promotions(self, platform_work_id: str | None = None) -> list[dict[str, Any]]:
        self._maybe_fail("fetch_promotions")
        return [promotion for promotion in self._load_fixture("promotions") if promotion["platform"] == self.platform]

    def fetch_coupons(self, platform_work_id: str | None = None) -> list[dict[str, Any]]:
        self._maybe_fail("fetch_coupons")
        return [coupon for coupon in self._load_fixture("coupons") if coupon["platform"] == self.platform]

    def fetch_rankings(self) -> list[dict[str, Any]]:
        self._maybe_fail("fetch_rankings")
        ranked = sorted(
            self.fetch_offers(None),
            key=lambda offer: (-int(offer["free_episode_count"]), int(offer["base_price_krw"]), str(offer["id"])),
        )
        return [
            {
                "rank": index + 1,
                "platform": self.platform,
                "platform_work_id": offer["platform_work_id"],
                "work_id": offer["work_id"],
                "offer_id": offer["id"],
            }
            for index, offer in enumerate(ranked)
        ]

    def _load_fixture(self, name: str) -> list[dict[str, Any]]:
        if self.fixture_root == FIXTURE_ROOT:
            return load_fixture(name)
        with (self.fixture_root / f"{name}.json").open(encoding="utf-8") as fixture_file:
            data = json.load(fixture_file)
        if not isinstance(data, list):
            raise ValueError(f"Fixture {name} must contain a JSON array")
        return data

    def _search_works(self, query: str) -> list[dict[str, Any]]:
        if self.fixture_root == FIXTURE_ROOT:
            return search_works(query)
        normalized_query = query.strip().casefold()
        works = self._load_fixture("works")
        if not normalized_query:
            return works
        return [
            work
            for work in works
            if normalized_query in work["title"].casefold()
            or any(normalized_query in author.casefold() for author in work["authors"])
        ]

    def _maybe_fail(self, method_name: str) -> None:
        remaining_failures = self.failure_plan.get(method_name, 0)
        if remaining_failures <= 0:
            return
        self.failure_plan[method_name] = remaining_failures - 1
        raise AdapterError(f"Simulated {self.adapter_name}.{method_name} failure")

    def _platform_work_id(self, work_id: str) -> str:
        return f"{PLATFORM_SLUGS[self.platform]}:{work_id}"

    def _normalize_platform_work_id(self, platform_work_id: str | None) -> str | None:
        if platform_work_id is None:
            return None
        return platform_work_id.split(":", 1)[1] if ":" in platform_work_id else platform_work_id

    def _with_platform_work_id(self, offer: dict[str, Any]) -> dict[str, Any]:
        enriched = dict(offer)
        enriched["platform_work_id"] = self._platform_work_id(str(offer["work_id"]))
        return enriched


class MockNaverWebtoonAdapter(FixturePlatformAdapter):
    """Fixture-only adapter for Naver Webtoon mock data."""

    platform = "네이버웹툰"
    adapter_name = "MockNaverWebtoonAdapter"


class MockKakaoPageAdapter(FixturePlatformAdapter):
    """Fixture-only adapter for KakaoPage mock data."""

    platform = "카카오페이지"
    adapter_name = "MockKakaoPageAdapter"


class MockRidiAdapter(FixturePlatformAdapter):
    """Fixture-only adapter for Ridi mock data."""

    platform = "리디"
    adapter_name = "MockRidiAdapter"


class MockCrawler:
    """Backward-compatible fixture offer reader used by older tests/imports."""

    def fetch_offers(self, work_id: str | None = None) -> list[dict[str, object]]:
        offers = load_fixture("offers")
        if work_id is None:
            return offers
        return [offer for offer in offers if offer["work_id"] == work_id]


@dataclass
class MockCrawlResult:
    """Records produced by one mock crawl run."""

    snapshot: dict[str, Any]
    price_history: list[dict[str, Any]] = field(default_factory=list)
    crawl_logs: list[dict[str, Any]] = field(default_factory=list)
    notification_events: list[dict[str, Any]] = field(default_factory=list)


def default_adapters(*, fixture_root: Path | None = None) -> list[PlatformAdapter]:
    """Create all MVP mock adapters."""

    return [
        MockNaverWebtoonAdapter(fixture_root=fixture_root),
        MockKakaoPageAdapter(fixture_root=fixture_root),
        MockRidiAdapter(fixture_root=fixture_root),
    ]


def run_mock_crawl(
    *,
    adapters: Iterable[PlatformAdapter] | None = None,
    fixture_root: Path | None = None,
    state_dir: Path | None = None,
    max_retries: int = 2,
    persist: bool = True,
) -> MockCrawlResult:
    """Run a deterministic fixture-only crawl and detect changes.

    If ``DATABASE_URL`` is set we still write the fixture-compatible local JSON
    state; live database writes can be added later behind that environment flag.
    """

    state_path = state_dir or DEFAULT_STATE_DIR
    adapter_list = list(adapters or default_adapters(fixture_root=fixture_root))
    previous_snapshot = _load_previous_snapshot(state_path) if persist else {"offers": {}}
    crawl_logs: list[dict[str, Any]] = []
    current_offers: dict[str, Any] = {}
    now = _utc_now()

    for adapter in adapter_list:
        started_at = _utc_now()
        items_seen = 0
        status = "success"
        notes: list[str] = ["fixture-only mock crawl"]
        try:
            rankings = _call_with_retry(adapter, "fetch_rankings", crawl_logs, max_retries=max_retries)
            items_seen += len(rankings)
            offers = _call_with_retry(adapter, "fetch_offers", crawl_logs, None, max_retries=max_retries)
            promotions = _call_with_retry(adapter, "fetch_promotions", crawl_logs, None, max_retries=max_retries)
            coupons = _call_with_retry(adapter, "fetch_coupons", crawl_logs, None, max_retries=max_retries)
            for offer in offers:
                _call_with_retry(adapter, "fetch_work_detail", crawl_logs, offer["platform_work_id"], max_retries=max_retries)
                calculated_price = calculate_offer_price(
                    paid_episode_price=offer["base_price_krw"],
                    currency_type="KRW",
                    free_episode_count=offer["free_episode_count"],
                    wait_free_available=offer["wait_free_available"],
                    promotions=promotions,
                    coupons=coupons,
                    current_timestamp=offer["last_verified_at"],
                )
                current_offers[offer["id"]] = {
                    "offer": offer,
                    "calculated_price": calculated_price,
                    "promotion_ids": sorted(str(promotion["id"]) for promotion in promotions),
                    "promotion_types": {
                        str(promotion["id"]): promotion.get("promotion_type") for promotion in promotions
                    },
                    "downloadable_coupon_ids": sorted(
                        str(coupon["id"]) for coupon in coupons if bool(coupon.get("downloadable"))
                    ),
                    "coupon_ids": sorted(str(coupon["id"]) for coupon in coupons),
                }
            items_seen += len(offers)
        except Exception as exc:  # noqa: BLE001 - crawl logs must capture any adapter failure.
            status = "failed"
            notes.append(f"adapter failed: {exc}")
        crawl_logs.append(
            _crawl_log(
                adapter=adapter,
                status=status,
                started_at=started_at,
                finished_at=_utc_now(),
                items_seen=items_seen,
                notes="; ".join(notes),
                error_message=None if status == "success" else notes[-1],
            )
        )

    snapshot = {
        "schema_version": 1,
        "generated_at": now,
        "database_url_present": bool(os.environ.get("DATABASE_URL")),
        "offers": current_offers,
    }
    changes = _detect_changes(previous_snapshot.get("offers", {}), current_offers, now)
    result = MockCrawlResult(
        snapshot=snapshot,
        price_history=changes["price_history"],
        crawl_logs=crawl_logs,
        notification_events=changes["notification_events"],
    )
    if persist:
        _persist_result(state_path, result)
    return result


def _call_with_retry(
    adapter: PlatformAdapter,
    method_name: str,
    crawl_logs: list[dict[str, Any]],
    *args: Any,
    max_retries: int,
) -> Any:
    method: Callable[..., Any] = getattr(adapter, method_name)
    for attempt in range(max_retries + 1):
        started_at = _utc_now()
        try:
            return method(*args)
        except AdapterError as exc:
            crawl_logs.append(
                _crawl_log(
                    adapter=adapter,
                    status="retrying" if attempt < max_retries else "failed",
                    started_at=started_at,
                    finished_at=_utc_now(),
                    items_seen=0,
                    error_message=str(exc),
                    notes=f"deterministic retry {attempt + 1} of {max_retries + 1} for {method_name}",
                )
            )
            if attempt >= max_retries:
                raise


def _detect_changes(previous: dict[str, Any], current: dict[str, Any], recorded_at: str) -> dict[str, list[dict[str, Any]]]:
    price_history: list[dict[str, Any]] = []
    notification_events: list[dict[str, Any]] = []
    price_fields = [
        "base_price",
        "instant_discounted_price",
        "coupon_expected_price",
        "cashback_adjusted_price",
        "effective_price_for_sort",
    ]

    for offer_id, current_entry in current.items():
        previous_entry = previous.get(offer_id)
        if previous_entry is None:
            continue
        current_price = current_entry["calculated_price"]
        previous_price = previous_entry.get("calculated_price", {})
        current_offer = current_entry["offer"]
        previous_offer = previous_entry.get("offer", {})

        changed_price_fields = [field for field in price_fields if current_price.get(field) != previous_price.get(field)]
        if changed_price_fields:
            price_history.append(_price_history_record(offer_id, current_price, recorded_at, changed_price_fields))

        if int(current_offer.get("free_episode_count", 0)) > int(previous_offer.get("free_episode_count", 0)):
            notification_events.append(
                _notification_event(
                    event_type="free_episode_count_increased",
                    offer_id=offer_id,
                    work_id=current_offer["work_id"],
                    payload={
                        "previous_free_episode_count": previous_offer.get("free_episode_count"),
                        "current_free_episode_count": current_offer.get("free_episode_count"),
                        "platform": current_offer["platform"],
                    },
                    created_at=recorded_at,
                )
            )

        if bool(current_offer.get("wait_free_available")) != bool(previous_offer.get("wait_free_available")):
            notification_events.append(
                _notification_event(
                    event_type="wait_free_availability_changed",
                    offer_id=offer_id,
                    work_id=current_offer["work_id"],
                    payload={
                        "previous_wait_free_available": previous_offer.get("wait_free_available"),
                        "current_wait_free_available": current_offer.get("wait_free_available"),
                        "platform": current_offer["platform"],
                    },
                    created_at=recorded_at,
                )
            )

        if int(current_price.get("instant_discounted_price", 0)) == 0 and int(previous_price.get("instant_discounted_price", 0)) > 0:
            notification_events.append(
                _notification_event(
                    event_type="work_became_free",
                    offer_id=offer_id,
                    work_id=current_offer["work_id"],
                    payload={"platform": current_offer["platform"]},
                    created_at=recorded_at,
                )
            )

        new_promotions = sorted(set(current_entry.get("promotion_ids", [])) - set(previous_entry.get("promotion_ids", [])))
        if new_promotions:
            notification_events.append(
                _notification_event(
                    event_type="new_promotion_started",
                    offer_id=offer_id,
                    work_id=current_offer["work_id"],
                    payload={"promotion_ids": new_promotions, "platform": current_offer["platform"]},
                    created_at=recorded_at,
                )
            )
            promotion_types = current_entry.get("promotion_types", {})
            instant_promotions = [promotion_id for promotion_id in new_promotions if promotion_types.get(promotion_id) == "instant_discount"]
            if instant_promotions:
                notification_events.append(
                    _notification_event(
                        event_type="instant_discount_promotion_started",
                        offer_id=offer_id,
                        work_id=current_offer["work_id"],
                        payload={"promotion_ids": instant_promotions, "platform": current_offer["platform"]},
                        created_at=recorded_at,
                    )
                )
            cashback_promotions = [promotion_id for promotion_id in new_promotions if promotion_types.get(promotion_id) == "cashback"]
            if cashback_promotions:
                notification_events.append(
                    _notification_event(
                        event_type="cashback_event_started",
                        offer_id=offer_id,
                        work_id=current_offer["work_id"],
                        payload={"promotion_ids": cashback_promotions, "platform": current_offer["platform"]},
                        created_at=recorded_at,
                    )
                )

        new_downloadable_coupons = sorted(
            set(current_entry.get("downloadable_coupon_ids", [])) - set(previous_entry.get("downloadable_coupon_ids", []))
        )
        if new_downloadable_coupons:
            notification_events.append(
                _notification_event(
                    event_type="new_downloadable_coupon",
                    offer_id=offer_id,
                    work_id=current_offer["work_id"],
                    payload={"coupon_ids": new_downloadable_coupons, "platform": current_offer["platform"]},
                    created_at=recorded_at,
                )
            )

        current_coupon_price = current_price.get("coupon_expected_price")
        previous_coupon_price = previous_price.get("coupon_expected_price")
        if current_coupon_price is not None and previous_coupon_price is not None and current_coupon_price < previous_coupon_price:
            notification_events.append(
                _notification_event(
                    event_type="coupon_expected_price_decreased",
                    offer_id=offer_id,
                    work_id=current_offer["work_id"],
                    payload={
                        "previous_coupon_expected_price": previous_coupon_price,
                        "current_coupon_expected_price": current_coupon_price,
                        "platform": current_offer["platform"],
                    },
                    created_at=recorded_at,
                )
            )

    return {"price_history": price_history, "notification_events": notification_events}


def _price_history_record(
    offer_id: str,
    calculated_price: dict[str, Any],
    recorded_at: str,
    changed_fields: list[str],
) -> dict[str, Any]:
    return {
        "id": str(uuid.uuid5(uuid.NAMESPACE_URL, offer_id + recorded_at)),
        "offer_id": offer_id,
        "base_price": calculated_price["base_price"],
        "instant_discounted_price": calculated_price["instant_discounted_price"],
        "coupon_expected_price": calculated_price["coupon_expected_price"],
        "cashback_adjusted_price": calculated_price["cashback_adjusted_price"],
        "effective_price_for_sort": calculated_price["effective_price_for_sort"],
        "recorded_at": recorded_at,
        "changed_fields": changed_fields,
    }


def _notification_event(
    *,
    event_type: str,
    offer_id: str,
    work_id: str,
    payload: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    return {
        "id": str(uuid.uuid5(uuid.NAMESPACE_URL, event_type + offer_id + created_at)),
        "notification_rule_id": None,
        "user_id": None,
        "work_id": work_id,
        "offer_id": offer_id,
        "event_type": event_type,
        "payload": payload,
        "email_to": None,
        "provider_message_id": None,
        "created_at": created_at,
    }


def _crawl_log(
    *,
    adapter: PlatformAdapter,
    status: str,
    started_at: str,
    finished_at: str,
    items_seen: int,
    error_message: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    return {
        "id": str(uuid.uuid4()),
        "platform_id": PLATFORM_SLUGS.get(adapter.platform, adapter.platform),
        "adapter_name": adapter.adapter_name,
        "status": status,
        "started_at": started_at,
        "finished_at": finished_at,
        "items_seen": items_seen,
        "error_message": error_message,
        "notes": notes,
    }


def _load_previous_snapshot(state_dir: Path) -> dict[str, Any]:
    snapshot_path = state_dir / "snapshot.json"
    if not snapshot_path.exists():
        return {"offers": {}}
    with snapshot_path.open(encoding="utf-8") as snapshot_file:
        data = json.load(snapshot_file)
    if not isinstance(data, dict):
        return {"offers": {}}
    return data


def _persist_result(state_dir: Path, result: MockCrawlResult) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    _write_json(state_dir / "snapshot.json", result.snapshot)
    _write_json(state_dir / "price_history.json", result.price_history)
    _write_json(state_dir / "crawl_logs.json", result.crawl_logs)
    _write_json(state_dir / "notification_events.json", result.notification_events)


def _write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as output_file:
        json.dump(payload, output_file, ensure_ascii=False, indent=2, sort_keys=True)
        output_file.write("\n")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def snapshot_for_fixtures(*, fixture_root: Path | None = None) -> dict[str, Any]:
    """Build a snapshot without reading or writing state; useful in tests."""

    return run_mock_crawl(fixture_root=fixture_root, persist=False).snapshot


def clone_jsonable(value: Any) -> Any:
    """Return a deep JSON-compatible copy for tests and fixture mutation."""

    return deepcopy(value)
