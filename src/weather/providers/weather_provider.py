from abc import ABC, abstractmethod


class WeatherProvider(ABC):
    @abstractmethod
    async def get_forecast(
        self, lat: float, lon: float, forecast_hours: int
    ):  # -> WeatherData
        pass
