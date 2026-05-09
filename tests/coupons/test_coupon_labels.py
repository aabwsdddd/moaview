from services.api.app.fixtures import load_fixture
from services.api.app.pricing import calculate_offer_price

NOW = "2026-05-09T00:00:00Z"


def coupon(**overrides):
    data = {
        "id": "coupon",
        "discount_type": "percent",
        "discount_value": 20,
        "downloadable": True,
        "starts_at": "2026-05-01T00:00:00Z",
        "ends_at": "2026-05-31T23:59:59Z",
    }
    data.update(overrides)
    return data


def price(coupons, paid_episode_price=1000):
    return calculate_offer_price(
        paid_episode_price=paid_episode_price,
        currency_type="KRW",
        free_episode_count=0,
        wait_free_available=False,
        promotions=[],
        coupons=coupons,
        current_timestamp=NOW,
    )


def test_user_action_coupons_are_expected_price_labels() -> None:
    coupons = load_fixture("coupons")

    for item in coupons:
        if item["requires_user_action"]:
            assert item["label"] == "쿠폰 적용 예상가"


def test_active_downloadable_percent_coupon() -> None:
    result = price([coupon(id="coupon_20")])

    assert result["coupon_expected_price"] == 800
    assert result["applied_coupon_ids"] == ["coupon_20"]
    assert result["price_confidence"] == "estimated"


def test_downloadable_coupon_respects_max_discount_amount() -> None:
    result = price([coupon(id="coupon_capped", discount_value=50, max_discount_amount=200)])

    assert result["coupon_expected_price"] == 800


def test_downloadable_coupon_with_min_purchase_amount_met() -> None:
    result = price([coupon(id="coupon_min_met", min_purchase_amount=900)])

    assert result["coupon_expected_price"] == 800
    assert result["applied_coupon_ids"] == ["coupon_min_met"]


def test_downloadable_coupon_with_min_purchase_amount_not_met() -> None:
    result = price([coupon(id="coupon_min_not_met", min_purchase_amount=1200)])

    assert result["coupon_expected_price"] is None
    assert result["effective_price_for_sort"] == 1000
    assert result["applied_coupon_ids"] == []
    assert "minimum purchase amount is not met" in result["calculation_note"]


def test_expired_coupon_does_not_apply() -> None:
    result = price([coupon(id="expired", ends_at="2026-05-08T23:59:59Z")])

    assert result["coupon_expected_price"] is None
    assert result["applied_coupon_ids"] == []


def test_future_coupon_does_not_apply() -> None:
    result = price([coupon(id="future", starts_at="2026-05-10T00:00:00Z")])

    assert result["coupon_expected_price"] is None
    assert result["applied_coupon_ids"] == []


def test_user_targeted_coupon_is_not_confirmed_or_applied() -> None:
    result = price([coupon(id="targeted", user_targeted=True)])

    assert result["coupon_expected_price"] is None
    assert result["effective_price_for_sort"] == 1000
    assert result["price_confidence"] == "user_targeted_unknown"
    assert "user-targeted" in result["calculation_note"]


def test_code_required_coupon_with_no_code_is_informational() -> None:
    result = price([coupon(id="code_missing", code_required=True, downloadable=False)])

    assert result["coupon_expected_price"] is None
    assert result["applied_coupon_ids"] == []
    assert "requires an unknown code" in result["calculation_note"]


def test_code_required_coupon_with_known_fixture_code_applies() -> None:
    result = price([coupon(id="code_known", code_required=True, downloadable=False, coupon_code="FIXTURE20")])

    assert result["coupon_expected_price"] == 800
    assert result["applied_coupon_ids"] == ["code_known"]


def test_multiple_coupons_select_best_valid_coupon() -> None:
    result = price(
        [
            coupon(id="coupon_10", discount_value=10),
            coupon(id="coupon_200", discount_type="amount", discount_value=200),
            coupon(id="coupon_targeted", discount_value=90, user_targeted=True),
        ]
    )

    assert result["coupon_expected_price"] == 800
    assert result["applied_coupon_ids"] == ["coupon_200"]


def test_coupon_type_downloadable_applies_to_expected_price_only() -> None:
    result = price(
        [
            {
                "id": "type_downloadable",
                "coupon_type": "downloadable",
                "discount_type": "percent",
                "discount_value": 20,
            }
        ]
    )

    assert result["instant_discounted_price"] == 1000
    assert result["coupon_expected_price"] == 800
    assert result["effective_price_for_sort"] == 800
    assert result["price_confidence"] == "estimated"
