import math
from dataclasses import dataclass
from datetime import datetime

MIN_PROB_VALUE = 0.0
MAX_PROB_VALUE = 100.0


@dataclass(frozen=True, slots=True)
class HourlyWeatherData:
    timestamp: datetime
    temperature: float
    apparent_temperature: float
    precipitation_probability: float
    precipitation: float
    uv_index: float
    weather_code: int

    def __post_init__(self):
        _validate_timestamp(self.timestamp)

        object.__setattr__(
            self,
            "temperature",
            _validate_finite_number(self.temperature, "Temperature"),
        )
        object.__setattr__(
            self,
            "apparent_temperature",
            _validate_finite_number(self.apparent_temperature, "Apparent temperature"),
        )
        object.__setattr__(
            self,
            "precipitation_probability",
            _validate_precipitation_probability(self.precipitation_probability),
        )
        object.__setattr__(
            self,
            "precipitation",
            _validate_non_negative_number(self.precipitation, "Precipitation"),
        )
        object.__setattr__(
            self, "uv_index", _validate_non_negative_number(self.uv_index, "UV index")
        )

        _validate_weather_code(self.weather_code)


def _validate_timestamp(value: datetime) -> None:
    if not isinstance(value, datetime):
        raise TypeError("Timestamp must be a datetime instance")


def _validate_finite_number(value: float, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field} must be a numeric value")

    if not math.isfinite(value):
        raise ValueError(f"{field} must be finite")

    return float(value)


def _validate_non_negative_number(value: float, field: str) -> float:
    validated_value = _validate_finite_number(value, field)

    if validated_value < 0:
        raise ValueError(f"{field} cannot be negative")

    return validated_value


def _validate_precipitation_probability(value: float) -> float:
    validated_value = _validate_finite_number(value, "Precipitation probability")

    if not MIN_PROB_VALUE <= validated_value <= MAX_PROB_VALUE:
        raise ValueError("Precipitation probability must be between 0 and 100")

    return validated_value


def _validate_weather_code(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("Weather code must be an integer")

    if value < 0:
        raise ValueError("Weather code cannot be negative")
