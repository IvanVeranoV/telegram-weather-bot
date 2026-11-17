from datetime import UTC, datetime

from httpx import AsyncClient

from src.weather.models.hourly_weather_data import HourlyWeatherData
from src.weather.models.weather_data import WeatherData
from src.weather.providers.weather_provider import WeatherProvider
from src.weather.providers.weather_provider_error import WeatherProviderError

URL_ENDPOINT = "https://api.open-meteo.com/v1/forecast"


class OpenMeteoProvider(WeatherProvider):
    def __init__(self, async_client: AsyncClient):
        self.async_client = async_client

    async def get_forecast(
        self, lat: float, lon: float, forecast_hours: int
    ) -> WeatherData:

        hourly_params = [
            "temperature_2m",
            "apparent_temperature",
            "precipitation_probability",
            "precipitation",
            "uv_index",
            "weather_code",
        ]

        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": hourly_params,
            "forecast_hours": forecast_hours,
            "timezone": "auto",
            "timeformat": "unixtime",
        }

        response = await self.async_client.get(url=URL_ENDPOINT, params=params)
        response.raise_for_status()

        json_response = response.json()

        try:
            return _check_response(json_response, forecast_hours)

        except (TypeError, ValueError, OverflowError) as error:
            raise WeatherProviderError("Invalid weather data") from error


def _check_response(unchecked_json_response: dict, forecast_hours: int) -> WeatherData:

    if not isinstance(unchecked_json_response, dict):
        raise WeatherProviderError

    required_keys = ["latitude", "longitude", "timezone", "elevation", "hourly"]

    for key in required_keys:
        if key not in unchecked_json_response:
            raise WeatherProviderError

    latitude = unchecked_json_response["latitude"]
    longitude = unchecked_json_response["longitude"]
    timezone = unchecked_json_response["timezone"]
    elevation = unchecked_json_response["elevation"]
    if not isinstance(unchecked_json_response["hourly"], dict):
        raise WeatherProviderError
    hourly_weather = _get_hourly_data(unchecked_json_response["hourly"], forecast_hours)

    return WeatherData(
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        elevation=elevation,
        hourly_weather=hourly_weather,
    )


def _get_hourly_data(json_hourly_data: dict, forecast_hours: int) -> tuple:
    # We will use forecast_hours as the number of elements that the arrays must haven (Ex: 24h = 24 elements)

    required_keys = [
        "temperature_2m",
        "apparent_temperature",
        "precipitation_probability",
        "precipitation",
        "uv_index",
        "weather_code",
        "time",
    ]

    for key in required_keys:
        if key not in json_hourly_data:
            raise WeatherProviderError
        if not isinstance(json_hourly_data[key], list):
            raise WeatherProviderError
        if len(json_hourly_data[key]) != forecast_hours:
            raise WeatherProviderError

    return tuple(
        HourlyWeatherData(
            timestamp=datetime.fromtimestamp(timestamp, tz=UTC),
            temperature=json_hourly_data["temperature_2m"][i],
            apparent_temperature=json_hourly_data["apparent_temperature"][i],
            precipitation_probability=json_hourly_data["precipitation_probability"][i],
            precipitation=json_hourly_data["precipitation"][i],
            uv_index=json_hourly_data["uv_index"][i],
            weather_code=json_hourly_data["weather_code"][i],
        )
        for i, timestamp in enumerate(json_hourly_data["time"])
    )
