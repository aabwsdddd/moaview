from services.api.app.catalog import get_work_detail, get_work_offers


def test_work_detail_includes_metadata_and_available_platforms() -> None:
    body = get_work_detail("work_moonlight_archive")

    assert body is not None
    assert body["title"] == "달빛 기록관"
    assert body["authors"] == ["한서윤"]
    assert body["content_type"] == "webtoon"
    assert body["status"] == "ongoing"
    assert body["description"] == "비밀스러운 기록관에서 시작되는 판타지 로맨스."
    assert [platform["label"] for platform in body["available_platforms"]] == ["네이버웹툰", "카카오페이지"]


def test_work_offers_include_flat_price_fields_and_active_terms() -> None:
    items = get_work_offers("work_moonlight_archive")

    assert items is not None
    assert len(items) == 2
    kakao = next(item for item in items if item["platform"] == "카카오페이지")
    assert kakao["source_url"] == "https://example.com/kakao/moonlight-archive"
    assert kakao["last_updated_at"] == "2026-05-01T09:10:00Z"
    assert kakao["free_episode_count"] == 7
    assert kakao["wait_free_available"] is True
    assert kakao["base_price"] == 400
    assert kakao["instant_discounted_price"] == 360
    assert kakao["coupon_expected_price"] == 324
    assert kakao["cashback_adjusted_price"] is None
    assert kakao["effective_price_for_sort"] == 324
    assert kakao["price_confidence"] == "estimated"
    assert kakao["active_promotions"][0]["id"] == "promo_kakao_spring_wait_free"
    assert kakao["active_coupons"][0]["id"] == "coupon_kakao_code_fixture"


def test_unknown_work_returns_none() -> None:
    assert get_work_detail("missing") is None
    assert get_work_offers("missing") is None
