from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from src.weather.models.hourly_weather_data import HourlyWeatherData


@pytest.fixture
def valid_weather_data():
    return {
        "timestamp": datetime(2026, 11, 16, 12, 0),
        "temperature": 18.5,
        "apparent_temperature": 17.2,
        "precipitation_probability": 35.0,
        "precipitation": 0.2,
        "uv_index": 3.5,
        "weather_code": 3,
    }


def test_creates_valid_instance(valid_weather_data):
    data = HourlyWeatherData(**valid_weather_data)

    assert data.temperature == 18.5
    assert data.weather_code == 3


def test_accepts_timezone_aware_timestamp(valid_weather_data):
    valid_weather_data["timestamp"] = datetime(2026, 11, 16, 12, 0, tzinfo=UTC)

    data = HourlyWeatherData(**valid_weather_data)

    assert data.timestamp.tzinfo == UTC


@pytest.mark.parametrize(
    "field",
    [
        "temperature",
        "apparent_temperature",
        "precipitation_probability",
        "precipitation",
        "uv_index",
    ],
)
@pytest.mark.parametrize("value", [10, 10.5])
def test_normalizes_numeric_values_to_float(valid_weather_data, field, value):
    valid_weather_data[field] = value

    data = HourlyWeatherData(**valid_weather_data)

    assert isinstance(getattr(data, field), float)


@pytest.mark.parametrize(
    "value",
    [True, False, "10", None],
)
def test_rejects_invalid_numeric_values(valid_weather_data, value):
    valid_weather_data["temperature"] = value

    with pytest.raises(TypeError):
        HourlyWeatherData(**valid_weather_data)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_rejects_non_finite_temperature(valid_weather_data, value):
    valid_weather_data["temperature"] = value

    with pytest.raises(ValueError):
        HourlyWeatherData(**valid_weather_data)


def test_rejects_invalid_timestamp(valid_weather_data):
    valid_weather_data["timestamp"] = "2026-11-16T12:00:00"

    with pytest.raises(TypeError):
        HourlyWeatherData(**valid_weather_data)


def test_rejects_negative_precipitation(valid_weather_data):
    valid_weather_data["precipitation"] = -0.1

    with pytest.raises(ValueError):
        HourlyWeatherData(**valid_weather_data)


@pytest.mark.parametrize("value", [0, 100])
def test_accepts_precipitation_probability_boundaries(valid_weather_data, value):
    valid_weather_data["precipitation_probability"] = value

    data = HourlyWeatherData(**valid_weather_data)

    assert data.precipitation_probability == float(value)


@pytest.mark.parametrize("value", [-0.1, 100.1])
def test_rejects_out_of_range_precipitation_probability(valid_weather_data, value):
    valid_weather_data["precipitation_probability"] = value

    with pytest.raises(ValueError):
        HourlyWeatherData(**valid_weather_data)


def test_rejects_negative_uv_index(valid_weather_data):
    valid_weather_data["uv_index"] = -1

    with pytest.raises(ValueError):
        HourlyWeatherData(**valid_weather_data)


@pytest.mark.parametrize("value", [True, 3.5, "3", None])
def test_rejects_invalid_weather_code(valid_weather_data, value):
    valid_weather_data["weather_code"] = value

    with pytest.raises(TypeError):
        HourlyWeatherData(**valid_weather_data)


def test_rejects_negative_weather_code(valid_weather_data):
    valid_weather_data["weather_code"] = -1

    with pytest.raises(ValueError):
        HourlyWeatherData(**valid_weather_data)


def test_instance_is_immutable(valid_weather_data):
    data = HourlyWeatherData(**valid_weather_data)

    with pytest.raises(FrozenInstanceError):
        data.temperature = 25.0
