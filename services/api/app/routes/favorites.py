"""Favorite routes for the fixture-backed MVP."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from services.api.app.favorites import FavoriteNotFoundError, add_favorite_work, list_favorite_works, remove_favorite_work

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.post("")
def add_favorite(payload: dict[str, Any]) -> dict[str, object]:
    """Add a fixture work to the in-memory favorites list."""

    try:
        return add_favorite_work(
            str(payload.get("work_id", "")),
            user_id=payload.get("user_id"),
            created_at=payload.get("created_at"),
        )
    except FavoriteNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{work_id}")
def remove_favorite(work_id: str) -> dict[str, object]:
    """Remove a fixture work from the in-memory favorites list."""

    return remove_favorite_work(work_id)


@router.get("")
def list_favorites() -> dict[str, object]:
    """List in-memory favorites with embedded work detail summaries."""

    return list_favorite_works()
