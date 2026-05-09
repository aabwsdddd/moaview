"""Admin MVP routes."""

from __future__ import annotations

from fastapi import APIRouter

from services.api.app.analytics import analytics_summary

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/analytics/summary")
def get_analytics_summary() -> dict[str, object]:
    """Return deterministic fixture-backed KPI summary for the admin dashboard."""

    return analytics_summary()
