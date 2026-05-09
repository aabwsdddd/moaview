from services.api.app.offers import list_calculated_offers


def test_offers_include_deterministic_calculated_price_contract() -> None:
    offers = list_calculated_offers("work_moonlight_archive")

    kakao_offer = next(offer for offer in offers if offer["platform"] == "카카오페이지")
    calculated_price = kakao_offer["calculated_price"]

    assert calculated_price["base_price"] == 400
    assert calculated_price["instant_discounted_price"] == 360
    assert calculated_price["coupon_expected_price"] == 324
    assert calculated_price["cashback_adjusted_price"] is None
    assert calculated_price["effective_price_for_sort"] == 324
    assert calculated_price["price_confidence"] == "estimated"
    assert calculated_price["applied_promotion_ids"] == ["promo_kakao_10_percent_auto"]
    assert calculated_price["applied_coupon_ids"] == ["coupon_kakao_code_fixture"]
    assert calculated_price["calculated_at"] == "2026-05-01T09:10:00Z"


def test_cashback_offer_keeps_sort_price_separate_from_cashback_adjusted_value() -> None:
    offers = list_calculated_offers("work_clockwork_palace")

    ridi_offer = offers[0]
    calculated_price = ridi_offer["calculated_price"]

    assert calculated_price["coupon_expected_price"] == 80
    assert calculated_price["cashback_adjusted_price"] == 64
    assert calculated_price["effective_price_for_sort"] == 80
    assert "not a direct discount" in calculated_price["calculation_note"]
