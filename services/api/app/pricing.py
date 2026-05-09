"""Deterministic pricing helpers for fixture-backed platform offers.

The pricing service is intentionally pure and fixture-oriented.  It does not
scrape or connect to production platforms. Confirmed prices include only base
price changes that are automatic for every visitor, while coupon and cashback
values remain separately labeled estimates.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Literal, TypedDict

PriceConfidence = Literal["confirmed", "estimated", "user_targeted_unknown"]


class OfferInput(TypedDict):
    base_price_krw: int
    instant_discount_krw: int
    coupon_expected_discount_krw: int
    cashback_rate: float


class PriceBreakdown(TypedDict):
    base_price_krw: int
    confirmed_price_krw: int
    coupon_expected_price_krw: int
    cashback_adjusted_price_krw: int


class PricingResult(TypedDict):
    base_price: int
    instant_discounted_price: int
    coupon_expected_price: int | None
    cashback_adjusted_price: int | None
    effective_price_for_sort: int
    price_confidence: PriceConfidence
    calculation_note: str
    applied_promotion_ids: list[str]
    applied_coupon_ids: list[str]
    calculated_at: str


def calculate_price_breakdown(offer: OfferInput) -> PriceBreakdown:
    """Return legacy labeled price levels for an offer.

    This compatibility wrapper keeps existing fixture tests working. New pricing
    code should use :func:`calculate_offer_price` so promotion and coupon terms
    are evaluated explicitly.
    """

    base_price = max(0, offer["base_price_krw"])
    confirmed_price = max(0, base_price - max(0, offer["instant_discount_krw"]))
    coupon_expected_price = max(0, confirmed_price - max(0, offer["coupon_expected_discount_krw"]))
    cashback_rate = min(max(offer["cashback_rate"], 0), 1)
    cashback_adjusted_price = round(coupon_expected_price * (1 - cashback_rate))

    return {
        "base_price_krw": base_price,
        "confirmed_price_krw": confirmed_price,
        "coupon_expected_price_krw": coupon_expected_price,
        "cashback_adjusted_price_krw": cashback_adjusted_price,
    }


def calculate_offer_price(
    *,
    paid_episode_price: int,
    currency_type: str,
    free_episode_count: int,
    wait_free_available: bool,
    promotions: list[dict[str, Any]] | None = None,
    coupons: list[dict[str, Any]] | None = None,
    current_timestamp: datetime | str | None = None,
) -> PricingResult:
    """Calculate deterministic offer price fields for a single paid episode.

    ``currency_type``, ``free_episode_count``, and ``wait_free_available`` are
    accepted as first-class inputs so API callers can keep the same contract as
    platform offers. The current MVP only uses them in the note; free episodes
    and wait-free availability never reduce the paid episode price directly.
    """

    calculated_at = _coerce_datetime(current_timestamp)
    base_price = max(0, int(paid_episode_price))
    active_promotions = [promotion for promotion in promotions or [] if _is_active(promotion, calculated_at)]
    active_coupons = [coupon for coupon in coupons or [] if _is_active(coupon, calculated_at)]

    instant_price = base_price
    applied_promotion_ids: list[str] = []
    notes: list[str] = [f"Base price is {base_price} {currency_type}."]

    for promotion in active_promotions:
        if promotion.get("promotion_type") != "instant_discount":
            continue
        discounted = _apply_discount(
            instant_price,
            discount_type=_discount_type_for(promotion),
            discount_value=promotion.get("discount_value"),
            discount_amount=promotion.get("discount_amount"),
            discount_percent=promotion.get("discount_percent"),
        )
        if discounted < instant_price:
            instant_price = discounted
            applied_promotion_ids.append(str(promotion.get("id")))

    if applied_promotion_ids:
        notes.append("Automatic instant discounts are treated as confirmed.")

    best_coupon = _select_best_coupon(active_coupons, instant_price)
    coupon_expected_price: int | None = None
    applied_coupon_ids: list[str] = []
    if best_coupon is not None:
        coupon_expected_price = best_coupon["price"]
        applied_coupon_ids.append(best_coupon["id"])
        notes.append("Coupon price is expected because coupon terms require user action or issuance.")

    cashback_base = coupon_expected_price if coupon_expected_price is not None else instant_price
    cashback = _best_cashback(active_promotions, cashback_base)
    cashback_adjusted_price: int | None = None
    if cashback is not None:
        cashback_adjusted_price = cashback["price"]
        applied_promotion_ids.append(cashback["id"])
        notes.append("Cashback is shown as an adjusted value, not a direct discount.")

    skipped_coupon_note = _coupon_skip_note(active_coupons, instant_price)
    if skipped_coupon_note:
        notes.append(skipped_coupon_note)

    if free_episode_count > 0:
        notes.append(f"{free_episode_count} free episodes are available before paid episode pricing.")
    if wait_free_available:
        notes.append("Wait-free availability is shown separately and does not reduce the paid episode price.")

    effective_price = coupon_expected_price if coupon_expected_price is not None else instant_price
    confidence: PriceConfidence = "estimated" if (coupon_expected_price is not None or cashback_adjusted_price is not None) else "confirmed"
    if any(_coupon_is_user_targeted(coupon) for coupon in active_coupons) and coupon_expected_price is None:
        confidence = "user_targeted_unknown"

    return {
        "base_price": base_price,
        "instant_discounted_price": instant_price,
        "coupon_expected_price": coupon_expected_price,
        "cashback_adjusted_price": cashback_adjusted_price,
        "effective_price_for_sort": effective_price,
        "price_confidence": confidence,
        "calculation_note": " ".join(notes),
        "applied_promotion_ids": _dedupe(applied_promotion_ids),
        "applied_coupon_ids": applied_coupon_ids,
        "calculated_at": calculated_at.isoformat().replace("+00:00", "Z"),
    }


def _select_best_coupon(coupons: list[dict[str, Any]], price: int) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    for coupon in coupons:
        if not _coupon_can_apply(coupon, price):
            continue
        coupon_price = _apply_discount(
            price,
            discount_type=str(coupon.get("discount_type", "amount")),
            discount_value=coupon.get("discount_value"),
            max_discount_amount=coupon.get("max_discount_amount"),
        )
        candidate = {"id": str(coupon.get("id")), "price": coupon_price}
        if best is None or (candidate["price"], candidate["id"]) < (best["price"], best["id"]):
            best = candidate
    return best


def _coupon_can_apply(coupon: dict[str, Any], price: int) -> bool:
    if _coupon_is_user_targeted(coupon):
        return False
    if _coupon_is_first_purchase_only(coupon) and not bool(coupon.get("first_purchase_known_eligible")):
        return False
    if _coupon_requires_code(coupon) and not (coupon.get("coupon_code") or coupon.get("known_code")):
        return False
    min_purchase_amount = coupon.get("min_purchase_amount")
    if min_purchase_amount is not None and price < int(min_purchase_amount):
        return False
    return _coupon_has_supported_expected_price_type(coupon)


def _coupon_skip_note(coupons: list[dict[str, Any]], price: int) -> str | None:
    reasons: list[str] = []
    for coupon in coupons:
        coupon_id = str(coupon.get("id"))
        if _coupon_is_user_targeted(coupon):
            reasons.append(f"{coupon_id} is user-targeted and not treated as confirmed.")
        elif _coupon_requires_code(coupon) and not (coupon.get("coupon_code") or coupon.get("known_code")):
            reasons.append(f"{coupon_id} requires an unknown code and is informational only.")
        elif _coupon_is_first_purchase_only(coupon) and not bool(coupon.get("first_purchase_known_eligible")):
            reasons.append(f"{coupon_id} depends on first-purchase account state and is informational only.")
        elif coupon.get("min_purchase_amount") is not None and price < int(coupon["min_purchase_amount"]):
            reasons.append(f"{coupon_id} minimum purchase amount is not met.")
    if not reasons:
        return None
    return " ".join(reasons)


def _best_cashback(promotions: list[dict[str, Any]], price: int) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    for promotion in promotions:
        if promotion.get("promotion_type") != "cashback":
            continue
        percent = _decimal(promotion.get("cashback_percent", promotion.get("discount_percent", 0)))
        if percent <= 0:
            continue
        adjusted_price = max(0, _money(Decimal(price) * (Decimal("1") - (percent / Decimal("100")))))
        candidate = {"id": str(promotion.get("id")), "price": adjusted_price}
        if best is None or (candidate["price"], candidate["id"]) < (best["price"], best["id"]):
            best = candidate
    return best


def _apply_discount(
    price: int,
    *,
    discount_type: str,
    discount_value: object = None,
    discount_amount: object = None,
    discount_percent: object = None,
    max_discount_amount: object = None,
) -> int:
    if discount_type in {"percent", "percentage"} or discount_percent is not None:
        percent = _decimal(discount_percent if discount_percent is not None else discount_value)
        discount = _money(Decimal(price) * (percent / Decimal("100")))
    else:
        discount = int(discount_amount if discount_amount is not None else discount_value or 0)
    if max_discount_amount is not None:
        discount = min(discount, int(max_discount_amount))
    return max(0, price - max(0, discount))


def _discount_type_for(item: dict[str, Any]) -> str:
    if item.get("discount_percent") is not None:
        return "percent"
    return str(item.get("discount_type", "amount"))


def _is_active(item: dict[str, Any], now: datetime) -> bool:
    starts_at = item.get("starts_at")
    ends_at = item.get("ends_at")
    if starts_at is not None and _coerce_datetime(starts_at) > now:
        return False
    if ends_at is not None and _coerce_datetime(ends_at) < now:
        return False
    return True


def _coupon_is_user_targeted(coupon: dict[str, Any]) -> bool:
    return bool(coupon.get("user_targeted") or coupon.get("coupon_type") == "user_targeted")


def _coupon_is_first_purchase_only(coupon: dict[str, Any]) -> bool:
    return bool(coupon.get("first_purchase_only") or coupon.get("coupon_type") == "first_purchase_only")


def _coupon_requires_code(coupon: dict[str, Any]) -> bool:
    return bool(coupon.get("code_required") or coupon.get("coupon_type") == "code_required")


def _coupon_has_supported_expected_price_type(coupon: dict[str, Any]) -> bool:
    coupon_type = coupon.get("coupon_type")
    return bool(
        coupon.get("downloadable")
        or coupon.get("auto_issued")
        or _coupon_requires_code(coupon)
        or coupon_type in {"downloadable", "auto_issued"}
    )


def _coerce_datetime(value: datetime | str | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(timezone.utc)


def _decimal(value: object) -> Decimal:
    return Decimal(str(value or 0))


def _money(value: Decimal) -> int:
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))
