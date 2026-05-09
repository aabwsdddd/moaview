from services.api.app.catalog import list_search_results


def test_api_search_finds_title_and_includes_comparison_summary() -> None:
    items = list_search_results("달빛")

    assert len(items) == 1
    item = items[0]
    assert item["id"] == "work_moonlight_archive"
    assert item["title"] == "달빛 기록관"
    assert item["authors"] == ["한서윤"]
    assert item["content_type"] == "webtoon"
    assert [platform["label"] for platform in item["platforms"]] == ["네이버웹툰", "카카오페이지"]
    assert item["max_free_episodes"] == 7
    assert item["lowest_confirmed_price"] == 300
    assert item["lowest_coupon_expected_price"] == 324
    assert item["best_platform_label"] == "네이버웹툰"


def test_api_search_finds_author() -> None:
    items = list_search_results("Studio Moa")

    assert len(items) == 1
    assert items[0]["id"] == "work_clockwork_palace"
