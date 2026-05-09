from services.api.app.fixtures import search_works


def test_search_finds_title() -> None:
    assert [work["id"] for work in search_works("달빛")] == ["work_moonlight_archive"]


def test_search_finds_author() -> None:
    assert [work["id"] for work in search_works("민도하")] == ["work_clockwork_palace"]
