from services.api.app.pricing import calculate_price_breakdown


def test_price_breakdown_keeps_coupon_and_cashback_separate() -> None:
    breakdown = calculate_price_breakdown(
        {
            "base_price_krw": 400,
            "instant_discount_krw": 50,
            "coupon_expected_discount_krw": 70,
            "cashback_rate": 0.05,
        }
    )

    assert breakdown == {
        "base_price_krw": 400,
        "confirmed_price_krw": 350,
        "coupon_expected_price_krw": 280,
        "cashback_adjusted_price_krw": 266,
    }
