from services.api.app.fixtures import load_fixture


def test_user_action_coupons_are_expected_price_labels() -> None:
    coupons = load_fixture("coupons")

    for coupon in coupons:
        if coupon["requires_user_action"]:
            assert coupon["label"] == "쿠폰 적용 예상가"
