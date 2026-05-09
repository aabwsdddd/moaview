"""MoaView FastAPI application using fixture data only."""

from __future__ import annotations

from fastapi import FastAPI

from services.api.app.fixtures import search_works
from services.api.app.health import health_payload
from services.api.app.offers import list_calculated_offers
from services.api.app.routes import admin, events, favorites, notifications, search, works

app = FastAPI(title="MoaView API", version="0.1.0")
app.include_router(search.router)
app.include_router(works.router)
app.include_router(favorites.router)
app.include_router(notifications.router)
app.include_router(events.router)
app.include_router(admin.router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Return API process health."""

    return health_payload()


@app.get("/works", tags=["works"])
def list_works(q: str = "") -> dict[str, object]:
    """Search fixture works by title or author."""

    works = search_works(q)
    return {"items": works, "count": len(works)}


@app.get("/offers", tags=["offers"])
def list_offers(work_id: str | None = None) -> dict[str, object]:
    """List fixture platform offers, optionally filtered by work."""

    offers = list_calculated_offers(work_id)
    return {"items": offers, "count": len(offers)}
