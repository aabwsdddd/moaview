"""MoaView FastAPI application using fixture data only."""

from __future__ import annotations

from fastapi import FastAPI

from services.api.app.fixtures import load_fixture, search_works
from services.api.app.health import health_payload

app = FastAPI(title="MoaView API", version="0.1.0")


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

    offers = load_fixture("offers")
    if work_id is not None:
        offers = [offer for offer in offers if offer["work_id"] == work_id]
    return {"items": offers, "count": len(offers)}
