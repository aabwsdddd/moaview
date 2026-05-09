"""Pricing helpers for fixture-backed platform offers.

Confirmed prices include only automatic discounts. Coupon and cashback values are
kept separate because they may require user action or represent estimated value.
"""

from __future__ import annotations

from typing import TypedDict


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


def calculate_price_breakdown(offer: OfferInput) -> PriceBreakdown:
    """Return labeled price levels for an offer without treating coupons as confirmed."""

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
