import math
from dataclasses import dataclass
from datetime import UTC, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.weather.models.hourly_weather_data import HourlyWeatherData


@dataclass(frozen=True, slots=True)
class WeatherData:
    latitude: float
    longitude: float
    timezone: str
    elevation: float
    hourly_weather: tuple[HourlyWeatherData, ...]

    def __post_init__(self):
        _validate_coordinate(self.latitude, "Latitude", -90, 90)
        _validate_coordinate(self.longitude, "Longitude", -180, 180)
        _validate_finite_number(self.elevation, "Elevation")
        _validate_timezone(self.timezone)
        _validate_hourly_weather(self.hourly_weather)


def _validate_finite_number(value: float, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field} must be numeric")

    if not math.isfinite(value):
        raise ValueError(f"{field} must be finite")


def _validate_coordinate(value: float, field: str, minimum: int, maximum: int) -> None:
    _validate_finite_number(value, field)

    if not minimum <= value <= maximum:
        raise ValueError(f"{field} must be between {minimum} and {maximum}")


def _validate_timezone(value: str) -> None:
    if not isinstance(value, str):
        raise TypeError("Timezone must be a string")

    try:
        ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError):
        raise ValueError(f"Invalid timezone: {value}") from None


def _validate_hourly_weather(value: tuple[HourlyWeatherData, ...]) -> None:
    if not isinstance(value, tuple):
        raise TypeError("Hourly weather must be a tuple")

    if not all(isinstance(item, HourlyWeatherData) for item in value):
        raise TypeError("Every item must be an HourlyWeatherData instance")

    timestamps = []

    for item in value:
        timestamp = item.timestamp

        if timestamp.utcoffset() != timedelta(0):
            raise ValueError("All timestamps must be normalized to UTC")

        timestamps.append(timestamp.astimezone(UTC))

    if len(timestamps) != len(set(timestamps)):
        raise ValueError("Hourly weather cannot contain duplicate timestamps")

    if timestamps != sorted(timestamps):
        raise ValueError("Hourly weather must be chronologically ordered")
