import asyncio
from datetime import UTC, datetime

from src.ai.services.weather_analysis_service import WeatherAnalysisService
from src.weather.models.hourly_weather_data import HourlyWeatherData
from src.weather.models.weather_data import WeatherData


def create_weather_data():
    hourly_weather = (
        HourlyWeatherData(
            timestamp=datetime(2026, 11, 18, 12, 0, tzinfo=UTC),
            temperature=18.5,
            apparent_temperature=18.0,
            precipitation_probability=70,
            precipitation=1.2,
            uv_index=2.0,
            weather_code=61,
        ),
        HourlyWeatherData(
            timestamp=datetime(2026, 11, 18, 13, 0, tzinfo=UTC),
            temperature=17.0,
            apparent_temperature=16.5,
            precipitation_probability=90,
            precipitation=2.4,
            uv_index=1.0,
            weather_code=63,
        ),
    )

    return WeatherData(
        latitude=40.4168,
        longitude=-3.7038,
        timezone="Europe/Madrid",
        elevation=667,
        hourly_weather=hourly_weather,
    )


def test_weather_analysis_service_sends_normalized_forecast_to_generator():
    class FakeTextGenerator:
        async def generate_text(self, prompt):
            self.prompt = prompt
            return "Se esperan lluvias durante las próximas horas."

    generator = FakeTextGenerator()
    service = WeatherAnalysisService(generator)

    result = asyncio.run(
        service.analyze(create_weather_data(), "Madrid, ES")
    )

    assert result == "Se esperan lluvias durante las próximas horas."
    assert "Madrid, ES" in generator.prompt
    assert "Europe/Madrid" in generator.prompt
    assert "temperatura 18.5 °C" in generator.prompt
    assert "probabilidad de precipitación 90 %" in generator.prompt
    assert "precipitación 2.4 mm" in generator.prompt
    assert "índice UV 1.0" in generator.prompt
