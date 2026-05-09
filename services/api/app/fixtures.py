"""Fixture loading and search utilities for the API scaffold."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FIXTURE_ROOT = Path(__file__).resolve().parents[3] / "packages" / "fixtures"


def load_fixture(name: str) -> list[dict[str, Any]]:
    """Load a fixture array by file stem."""

    with (FIXTURE_ROOT / f"{name}.json").open(encoding="utf-8") as fixture_file:
        data = json.load(fixture_file)
    if not isinstance(data, list):
        raise ValueError(f"Fixture {name} must contain a JSON array")
    return data


def search_works(query: str) -> list[dict[str, Any]]:
    """Search works by title or author using fixture data."""

    normalized_query = query.strip().casefold()
    works = load_fixture("works")
    if not normalized_query:
        return works
    return [
        work
        for work in works
        if normalized_query in work["title"].casefold()
        or any(normalized_query in author.casefold() for author in work["authors"])
    ]


def promotions_for_platform(platform: str) -> list[dict[str, Any]]:
    """Return fixture promotions for a platform display name."""

    return [promotion for promotion in load_fixture("promotions") if promotion["platform"] == platform]


def coupons_for_platform(platform: str) -> list[dict[str, Any]]:
    """Return fixture coupons for a platform display name."""

    return [coupon for coupon in load_fixture("coupons") if coupon["platform"] == platform]
