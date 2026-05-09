from services.api.app.pricing import calculate_offer_price, calculate_price_breakdown

NOW = "2026-05-09T00:00:00Z"


def price(promotions=None, coupons=None, paid_episode_price=1000):
    return calculate_offer_price(
        paid_episode_price=paid_episode_price,
        currency_type="KRW",
        free_episode_count=3,
        wait_free_available=True,
        promotions=promotions or [],
        coupons=coupons or [],
        current_timestamp=NOW,
    )


def promo(**overrides):
    data = {
        "id": "promo",
        "promotion_type": "instant_discount",
        "starts_at": "2026-05-01T00:00:00Z",
        "ends_at": "2026-05-31T23:59:59Z",
    }
    data.update(overrides)
    return data


def test_legacy_price_breakdown_keeps_coupon_and_cashback_separate() -> None:
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


def test_no_promotion_or_coupon() -> None:
    result = price()

    assert result["base_price"] == 1000
    assert result["instant_discounted_price"] == 1000
    assert result["coupon_expected_price"] is None
    assert result["cashback_adjusted_price"] is None
    assert result["effective_price_for_sort"] == 1000
    assert result["price_confidence"] == "confirmed"


def test_automatic_percent_instant_discount_is_confirmed() -> None:
    result = price(promotions=[promo(id="promo_10", discount_percent=10)])

    assert result["instant_discounted_price"] == 900
    assert result["effective_price_for_sort"] == 900
    assert result["price_confidence"] == "confirmed"
    assert result["applied_promotion_ids"] == ["promo_10"]


def test_fixed_amount_instant_discount_is_confirmed() -> None:
    result = price(promotions=[promo(id="promo_100", discount_amount=100)])

    assert result["instant_discounted_price"] == 900
    assert result["effective_price_for_sort"] == 900
    assert result["applied_promotion_ids"] == ["promo_100"]


def test_expired_and_future_promotions_do_not_apply() -> None:
    result = price(
        promotions=[
            promo(id="expired", discount_percent=99, ends_at="2026-05-08T23:59:59Z"),
            promo(id="future", discount_percent=99, starts_at="2026-05-10T00:00:00Z"),
        ]
    )

    assert result["instant_discounted_price"] == 1000
    assert result["applied_promotion_ids"] == []


def test_cashback_only_is_adjusted_value_not_direct_discount() -> None:
    result = price(promotions=[promo(id="cashback_5", promotion_type="cashback", cashback_percent=5)])

    assert result["instant_discounted_price"] == 1000
    assert result["cashback_adjusted_price"] == 950
    assert result["effective_price_for_sort"] == 1000
    assert result["price_confidence"] == "estimated"
    assert "not a direct discount" in result["calculation_note"]


def test_instant_discount_plus_coupon() -> None:
    result = price(
        promotions=[promo(id="promo_10", discount_percent=10)],
        coupons=[
            {
                "id": "coupon_20",
                "discount_type": "percent",
                "discount_value": 20,
                "downloadable": True,
                "starts_at": "2026-05-01T00:00:00Z",
                "ends_at": "2026-05-31T23:59:59Z",
            }
        ],
    )

    assert result["instant_discounted_price"] == 900
    assert result["coupon_expected_price"] == 720
    assert result["effective_price_for_sort"] == 720
    assert result["price_confidence"] == "estimated"


def test_coupon_plus_cashback() -> None:
    result = price(
        promotions=[promo(id="cashback_10", promotion_type="cashback", cashback_percent=10)],
        coupons=[
            {
                "id": "coupon_100",
                "discount_type": "amount",
                "discount_value": 100,
                "downloadable": True,
            }
        ],
    )

    assert result["coupon_expected_price"] == 900
    assert result["cashback_adjusted_price"] == 810
    assert result["effective_price_for_sort"] == 900
