import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from src.telegram_bot.bot import AWAITING_QUERY, LAST_LOCATION, TelegramBot
from src.weather.models.hourly_weather_data import HourlyWeatherData
from src.weather.models.weather_data import WeatherData


def create_bot():
    return TelegramBot.__new__(TelegramBot)


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
    )

    return WeatherData(
        latitude=40.4168,
        longitude=-3.7038,
        timezone="Europe/Madrid",
        elevation=667,
        hourly_weather=hourly_weather,
    )


def test_search_without_arguments_activates_awaiting_query():
    bot = create_bot()

    update = SimpleNamespace(message=SimpleNamespace(reply_text=AsyncMock()))

    context = SimpleNamespace(args=[], user_data={})

    asyncio.run(bot.search(update, context))

    assert context.user_data[AWAITING_QUERY] is True
    update.message.reply_text.assert_awaited_once_with("¿Qué ciudad quieres consultar?")


def test_handle_search_query_processes_city():
    bot = create_bot()

    update = SimpleNamespace(
        message=SimpleNamespace(text="Madrid", reply_text=AsyncMock())
    )

    geocoding_provider = SimpleNamespace(search=AsyncMock(return_value=[]))

    context = SimpleNamespace(
        user_data={AWAITING_QUERY: True},
        application=SimpleNamespace(
            bot_data={"geocoding_provider": geocoding_provider}
        ),
    )

    asyncio.run(bot.handle_search_query(update, context))

    geocoding_provider.search.assert_awaited_once_with("Madrid")
    assert AWAITING_QUERY not in context.user_data


def test_cancel_removes_awaiting_query():
    bot = create_bot()

    update = SimpleNamespace(message=SimpleNamespace(reply_text=AsyncMock()))

    context = SimpleNamespace(user_data={AWAITING_QUERY: True})

    asyncio.run(bot.cancel(update, context))

    assert AWAITING_QUERY not in context.user_data
    update.message.reply_text.assert_awaited_once()


def test_normal_message_without_search_is_ignored():
    bot = create_bot()

    update = SimpleNamespace(
        message=SimpleNamespace(text="Madrid", reply_text=AsyncMock())
    )

    context = SimpleNamespace(user_data={})

    asyncio.run(bot.handle_search_query(update, context))

    update.message.reply_text.assert_not_awaited()


def test_run_uses_polling_in_development():
    bot = create_bot()
    bot.settings = SimpleNamespace(environment="development")
    bot.application = Mock()

    bot.run()

    bot.application.run_polling.assert_called_once_with()
    bot.application.run_webhook.assert_not_called()


def test_run_uses_webhook_in_staging_and_production():
    bot = create_bot()
    bot.settings = SimpleNamespace(
        environment="staging",
        webhook_url="https://example.com",
        webhook_secret="test-secret",
        port=8080,
    )
    bot.application = Mock()

    bot.run()

    bot.application.run_webhook.assert_called_once_with(
        listen="0.0.0.0",
        port=8080,
        webhook_url="https://example.com",
        secret_token="test-secret",
    )
    bot.application.run_polling.assert_not_called()


def test_forecast_sends_weather_and_ai_analysis():
    bot = create_bot()
    bot.logger = Mock()

    location = SimpleNamespace(
        latitude=40.4168,
        longitude=-3.7038,
        name="Madrid",
        country="ES",
    )
    weather_data = create_weather_data()
    weather_provider = SimpleNamespace(
        get_forecast=AsyncMock(return_value=weather_data)
    )
    analysis_service = SimpleNamespace(
        analyze=AsyncMock(return_value="Se esperan lluvias. Lleva paraguas.")
    )
    message = SimpleNamespace(reply_text=AsyncMock())
    update = SimpleNamespace(message=message)
    context = SimpleNamespace(
        user_data={LAST_LOCATION: location},
        application=SimpleNamespace(
            bot_data={
                "weather_provider": weather_provider,
                "weather_analysis_service": analysis_service,
            }
        ),
    )

    asyncio.run(bot.forecast(update, context))

    weather_provider.get_forecast.assert_awaited_once_with(
        location.latitude,
        location.longitude,
        24,
    )
    analysis_service.analyze.assert_awaited_once_with(
        weather_data,
        "Madrid, ES",
    )
    assert message.reply_text.await_count == 2
    assert message.reply_text.await_args_list[0].kwargs["parse_mode"] == "HTML"
    assert message.reply_text.await_args_list[1].args[0].startswith("🤖 Análisis IA")
    assert message.reply_text.await_args_list[1].kwargs["parse_mode"] is None


def test_forecast_sends_weather_when_ai_analysis_fails():
    bot = create_bot()
    bot.logger = Mock()

    location = SimpleNamespace(
        latitude=40.4168,
        longitude=-3.7038,
        name="Madrid",
        country="ES",
    )
    weather_provider = SimpleNamespace(
        get_forecast=AsyncMock(return_value=create_weather_data())
    )
    analysis_service = SimpleNamespace(
        analyze=AsyncMock(side_effect=RuntimeError("Gemini unavailable"))
    )
    message = SimpleNamespace(reply_text=AsyncMock())
    update = SimpleNamespace(message=message)
    context = SimpleNamespace(
        user_data={LAST_LOCATION: location},
        application=SimpleNamespace(
            bot_data={
                "weather_provider": weather_provider,
                "weather_analysis_service": analysis_service,
            }
        ),
    )

    asyncio.run(bot.forecast(update, context))

    assert message.reply_text.await_count == 1
    assert message.reply_text.await_args.kwargs["parse_mode"] == "HTML"


def test_forecast_sends_weather_when_ai_is_not_configured():
    bot = create_bot()
    bot.logger = Mock()

    location = SimpleNamespace(
        latitude=40.4168,
        longitude=-3.7038,
        name="Madrid",
        country="ES",
    )
    weather_provider = SimpleNamespace(
        get_forecast=AsyncMock(return_value=create_weather_data())
    )
    message = SimpleNamespace(reply_text=AsyncMock())
    update = SimpleNamespace(message=message)
    context = SimpleNamespace(
        user_data={LAST_LOCATION: location},
        application=SimpleNamespace(
            bot_data={"weather_provider": weather_provider}
        ),
    )

    asyncio.run(bot.forecast(update, context))

    assert message.reply_text.await_count == 1
    weather_provider.get_forecast.assert_awaited_once()
