import asyncio

import httpx
import pytest

from src.geocoding.models.location_candidate import OSMType
from src.geocoding.providers.nominatim_provider import NominatimProvider


def create_candidate(
    name="Madrid",
    latitude="40.4167820",
    longitude="-3.7035070",
    country_code="es",
    osm_type="relation",
    osm_id=5326784,
    state="Comunidad de Madrid",
):
    return {
        "name": name,
        "lat": latitude,
        "lon": longitude,
        "osm_type": osm_type,
        "osm_id": osm_id,
        "address": {
            "country_code": country_code,
            "state": state,
        },
    }


def execute_search(payload, status_code=200):
    def handler(request):
        return httpx.Response(status_code, json=payload)

    async def run():
        transport = httpx.MockTransport(handler)

        async with httpx.AsyncClient(transport=transport) as client:
            provider = NominatimProvider(client)
            return await provider.search("Madrid")

    return asyncio.run(run())


def test_search_returns_valid_candidates():
    candidates = execute_search([create_candidate()])

    assert len(candidates) == 1

    candidate = candidates[0]

    assert candidate.name == "Madrid"
    assert candidate.country == "ES"
    assert candidate.latitude == 40.416782
    assert candidate.longitude == -3.703507
    assert candidate.osm_type == OSMType.RELATION
    assert candidate.osm_id == 5326784
    assert candidate.region == "Comunidad de Madrid"


def test_search_returns_empty_list():
    candidates = execute_search([])

    assert candidates == []


def test_search_discards_invalid_candidate_and_keeps_valid_ones():
    payload = [
        create_candidate(name="Madrid"),
        create_candidate(name="Invalid", latitude="abc"),
        create_candidate(name="Berlin", country_code="de"),
    ]

    candidates = execute_search(payload)

    assert len(candidates) == 2
    assert candidates[0].name == "Madrid"
    assert candidates[1].name == "Berlin"


def test_search_returns_empty_list_when_all_candidates_are_invalid():
    payload = [
        create_candidate(latitude="abc"),
        create_candidate(latitude="999"),
        create_candidate(osm_type="unknown"),
    ]

    candidates = execute_search(payload)

    assert candidates == []


def test_search_propagates_http_errors():
    with pytest.raises(httpx.HTTPStatusError):
        execute_search([], status_code=500)
