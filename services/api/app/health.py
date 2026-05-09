"""Health contract helpers for the API."""


def health_payload() -> dict[str, str]:
    """Return API process health payload."""

    return {"status": "ok", "service": "api"}
