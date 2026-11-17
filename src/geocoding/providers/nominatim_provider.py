from httpx import AsyncClient

from src.geocoding.models.location_candidate import LocationCandidate, OSMType
from src.geocoding.providers.geocoding_provider import GeocodingProvider

URL_ENDPOINT: str = "https://nominatim.openstreetmap.org/search"
RESPONSE_FORMAT: str = "jsonv2"
ADDRESS_DETAILS: int = 1


class NominatimProvider(GeocodingProvider):
    async_client: AsyncClient

    def __init__(
        self,
        async_client: AsyncClient,
    ):
        self.async_client = async_client

    async def search(self, query: str, limit: int = 5) -> list[LocationCandidate]:
        params: dict[str, str | int] = {
            "q": query,
            "format": RESPONSE_FORMAT,
            "addressdetails": ADDRESS_DETAILS,
            "limit": limit,
        }
        response = await self.async_client.get(url=URL_ENDPOINT, params=params)
        response.raise_for_status()
        json_response = response.json()
        location_candidates: list[LocationCandidate] = []
        for candidate in json_response:
            try:
                location_candidates.append(
                    LocationCandidate(
                        name=candidate["name"],
                        country=candidate["address"]["country_code"],
                        latitude=float(candidate["lat"]),
                        longitude=float(candidate["lon"]),
                        osm_type=OSMType(candidate["osm_type"].lower()),
                        osm_id=candidate["osm_id"],
                        region=candidate["address"].get("state"),
                    )
                )
            except (ValueError, TypeError, KeyError) as error:
                print(f"Candidato descartado: {error}")
                continue
        return location_candidates
