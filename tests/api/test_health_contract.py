from services.api.app.health import health_payload


def test_health_contract() -> None:
    assert health_payload() == {"status": "ok", "service": "api"}
