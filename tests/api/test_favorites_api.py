import pytest

from services.api.app.favorites import (
    FavoriteNotFoundError,
    add_favorite_work,
    list_favorite_works,
    remove_favorite_work,
    reset_favorites,
)


def setup_function() -> None:
    reset_favorites()


def test_add_list_and_delete_favorite_work() -> None:
    add_body = add_favorite_work("work_moonlight_archive")

    assert add_body["item"]["work_id"] == "work_moonlight_archive"

    body = list_favorite_works()
    assert body["count"] == 1
    assert body["items"][0]["work"]["title"] == "달빛 기록관"

    delete_body = remove_favorite_work("work_moonlight_archive")
    assert delete_body["count"] == 0


def test_favorite_unknown_work_returns_404() -> None:
    with pytest.raises(FavoriteNotFoundError):
        add_favorite_work("missing")
