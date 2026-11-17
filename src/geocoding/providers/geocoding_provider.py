from abc import ABC, abstractmethod

from src.geocoding.models.location_candidate import LocationCandidate


class GeocodingProvider(ABC):
    @abstractmethod
    async def search(self, query: str, limit: int = 5) -> list[LocationCandidate]:
        pass
