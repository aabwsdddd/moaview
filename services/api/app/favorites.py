"""In-memory favorite store for the fixture-backed API MVP."""

from __future__ import annotations

from typing import Any

from services.api.app.catalog import get_work, get_work_detail

FAVORITE_USER_ID = "fixture_user"
FIXTURE_TIMESTAMP = "2026-05-09T00:00:00Z"

_FAVORITES: dict[str, dict[str, Any]] = {}


class FavoriteNotFoundError(ValueError):
    """Raised when a favorite request references an unknown fixture work."""


def reset_favorites() -> None:
    """Clear in-memory favorites for deterministic tests."""

    _FAVORITES.clear()


def add_favorite_work(work_id: str, *, user_id: str | None = None, created_at: str | None = None) -> dict[str, object]:
    """Add a fixture work to the in-memory favorites list."""

    if get_work(work_id) is None:
        raise FavoriteNotFoundError("Work not found")

    favorite = _FAVORITES.setdefault(
        work_id,
        {
            "user_id": user_id or FAVORITE_USER_ID,
            "work_id": work_id,
            "created_at": created_at or FIXTURE_TIMESTAMP,
        },
    )
    return {"item": _favorite_response(favorite), "count": len(_FAVORITES)}


def remove_favorite_work(work_id: str) -> dict[str, object]:
    """Remove a fixture work from the in-memory favorites list."""

    _FAVORITES.pop(work_id, None)
    return {"deleted": True, "work_id": work_id, "count": len(_FAVORITES)}


def list_favorite_works() -> dict[str, object]:
    """List in-memory favorites with embedded work detail summaries."""

    items = [_favorite_response(favorite) for favorite in _FAVORITES.values()]
    return {"items": items, "count": len(items)}


def _favorite_response(favorite: dict[str, Any]) -> dict[str, Any]:
    response = dict(favorite)
    response["work"] = get_work_detail(favorite["work_id"])
    return response
