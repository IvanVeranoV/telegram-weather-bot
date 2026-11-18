from zoneinfo import ZoneInfo

from src.weather.models.weather_data import WeatherData


class WeatherAnalysisService:
    """Build a grounded weather summary and delegate its interpretation."""

    def __init__(self, text_generator):
        self.text_generator = text_generator

    async def analyze(self, weather_data: WeatherData, location_name: str) -> str:
        timezone = ZoneInfo(weather_data.timezone)
        forecast_lines = []

        for hour in weather_data.hourly_weather:
            local_time = hour.timestamp.astimezone(timezone)

            forecast_lines.append(
                f"- {local_time.strftime('%d/%m %H:%M')}: "
                f"temperatura {hour.temperature:.1f} °C; "
                f"sensación térmica {hour.apparent_temperature:.1f} °C; "
                f"probabilidad de precipitación "
                f"{hour.precipitation_probability:.0f} %; "
                f"precipitación {hour.precipitation:.1f} mm; "
                f"índice UV {hour.uv_index:.1f}."
            )

        prompt = (
            f"Ubicación: {location_name}\n"
            f"Zona horaria: {weather_data.timezone}\n"
            "Pronóstico horario normalizado para las próximas 24 horas:\n"
            f"{chr(10).join(forecast_lines)}\n\n"
            "Analiza la evolución durante el periodo disponible. Destaca solo "
            "los cambios y riesgos relevantes y termina con recomendaciones "
            "prácticas. No añadas valores que no aparezcan en los datos."
        )

        return await self.text_generator.generate_text(prompt)
