"""Work detail and offer comparison routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from services.api.app.catalog import get_work_detail, get_work_offers

router = APIRouter(prefix="/api/works", tags=["works"])


@router.get("/{work_id}")
def work_detail(work_id: str) -> dict[str, object]:
    """Return fixture-backed work detail metadata."""

    work = get_work_detail(work_id)
    if work is None:
        raise HTTPException(status_code=404, detail="Work not found")
    return work


@router.get("/{work_id}/offers")
def work_offers(work_id: str) -> dict[str, object]:
    """Return platform comparison offers for a fixture work."""

    offers = get_work_offers(work_id)
    if offers is None:
        raise HTTPException(status_code=404, detail="Work not found")
    return {"items": offers, "count": len(offers)}
