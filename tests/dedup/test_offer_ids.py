from services.api.app.fixtures import load_fixture


def test_offer_ids_are_unique() -> None:
    offers = load_fixture("offers")
    offer_ids = [offer["id"] for offer in offers]

    assert len(offer_ids) == len(set(offer_ids))
