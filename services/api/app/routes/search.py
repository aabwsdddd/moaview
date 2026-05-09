"""Search routes for the fixture-backed API."""

from __future__ import annotations

from fastapi import APIRouter

from services.api.app.catalog import list_search_results

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search")
def search(q: str = "") -> dict[str, object]:
    """Search fixture works by title or author with comparison summary fields."""

    items = list_search_results(q)
    return {"items": items, "count": len(items)}
