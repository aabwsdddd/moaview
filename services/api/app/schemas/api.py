"""Lightweight schema aliases for documented fixture API payloads."""

from __future__ import annotations

from typing import Any, TypeAlias

JsonObject: TypeAlias = dict[str, Any]
JsonArray: TypeAlias = list[JsonObject]
