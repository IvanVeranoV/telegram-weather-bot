import logging
from datetime import timedelta
from zoneinfo import ZoneInfo

from httpx import AsyncClient
from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.geocoding.providers.nominatim_provider import NominatimProvider
from src.weather.providers.open_meteo_provider import OpenMeteoProvider
from src.weather.providers.weather_provider_error import (
    WeatherConnectionError,
    WeatherProviderError,
    WeatherRateLimitError,
    WeatherServiceUnavailableError,
    WeatherTimeoutError,
)

USER_AGENT = "BotTelegramTiempo/0.1"
PENDING_LOCATIONS = "pending_locations"
AWAITING_QUERY = "awaiting_query"
DEFAULT_FORECAST_HOURS = 24
LAST_LOCATION = "last_location"
SUMMARY_HOURS = 4


class TelegramBot:
    logger = logging.getLogger(__name__)

    def __init__(self, settings):
        self.settings = settings

        token = settings.telegram_bot_token
        if not token or token.strip() == "" or " " in token:
            raise ValueError("No se ha encontrado el token de Telegram")

        self.application = (
            Application.builder()
            .token(token)
            .post_init(self._post_init)
            .post_shutdown(self._post_shutdown)
            .build()
        )

        self._register_handlers()

    async def _post_init(self, application: Application):
        commands = [
            BotCommand("start", "Iniciar el bot"),
            BotCommand("search", "Buscar el tiempo de una ciudad"),
            BotCommand("forecast", "Consultar el pronóstico completo de 24 horas"),
            BotCommand("cancel", "Cancelar búsqueda actual"),
        ]

        await application.bot.set_my_commands(commands)

        async_client = AsyncClient(headers={"User-Agent": USER_AGENT})
        application.bot_data["async_client"] = async_client
        application.bot_data["geocoding_provider"] = NominatimProvider(async_client)
        application.bot_data["weather_provider"] = OpenMeteoProvider(async_client)

    async def _post_shutdown(self, application: Application):
        async_client = application.bot_data.get("async_client")
        if async_client:
            await async_client.aclose()

    def _register_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("search", self.search))
        self.application.add_handler(CommandHandler("forecast", self.forecast))
        self.application.add_handler(CommandHandler("cancel", self.cancel))

        self.application.add_error_handler(self._handle_error)

        self.application.add_handler(
            CallbackQueryHandler(
                self.select_location,
                pattern=r"^location:",
            )
        )

        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_search_query,
            )
        )

    async def _handle_error(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        error = context.error

        if isinstance(error, WeatherRateLimitError):
            if error.retry_after is not None:
                update_reply_message = (
                    "Se ha alcanzado el límite de consultas del servicio "
                    f"meteorológico. Inténtalo de nuevo en "
                    f"{timedelta(seconds=error.retry_after)}"
                )
            else:
                update_reply_message = (
                    "Se ha alcanzado el límite de consultas del servicio "
                    "meteorológico. Inténtalo de nuevo más tarde"
                )

        elif isinstance(error, WeatherTimeoutError):
            update_reply_message = (
                "La consulta meteorológica está tardando más de lo esperado. "
                "Inténtalo de nuevo en unos instantes"
            )

        elif isinstance(error, WeatherServiceUnavailableError):
            update_reply_message = (
                "El servicio meteorológico no está disponible temporalmente. "
                "Inténtalo de nuevo más tarde"
            )

        elif isinstance(error, WeatherConnectionError):
            update_reply_message = (
                "No hemos podido conectar con el servicio meteorológico. "
                "Comprueba tu conexión e inténtalo de nuevo"
            )

        elif isinstance(error, WeatherProviderError):
            update_reply_message = (
                "No hemos podido obtener los datos meteorológicos "
                "correctamente. Inténtalo de nuevo más tarde"
            )

        else:
            update_reply_message = (
                "Ha ocurrido un error inesperado al procesar tu solicitud. "
                "Inténtalo de nuevo más tarde"
            )

        self.logger.error(
            "Error while processing update",
            exc_info=(type(error), error, error.__traceback__),
        )

        if update and update.effective_message:
            await update.effective_message.reply_text(update_reply_message)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("¡Hola! 🌤️ Soy tu asistente meteorológico.")

    async def search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if PENDING_LOCATIONS in context.user_data:
            await update.message.reply_text(
                "Tienes una selección pendiente. "
                "Selecciona una ubicación o utiliza /cancel para cancelarla."
            )
            return

        query = " ".join(context.args).strip()

        if not query:
            context.user_data[AWAITING_QUERY] = True
            await update.message.reply_text("¿Qué ciudad quieres consultar?")
            return

        context.user_data.pop(AWAITING_QUERY, None)
        await self._process_search_query(update, context, query)

    async def handle_search_query(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        if AWAITING_QUERY not in context.user_data:
            return

        if PENDING_LOCATIONS in context.user_data:
            return

        query = update.message.text.strip()

        if not query:
            await update.message.reply_text(
                "Por favor, indica el nombre de una ciudad."
            )
            return

        context.user_data.pop(AWAITING_QUERY, None)
        await self._process_search_query(update, context, query)

    async def _process_search_query(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        query: str,
    ):
        geocoding_provider = context.application.bot_data["geocoding_provider"]
        locations = await geocoding_provider.search(query)

        if not locations:
            await update.message.reply_text(
                f"No he encontrado ubicaciones para '{query}'."
            )
            return

        if len(locations) == 1:
            await self._send_forecast(update.message, context, locations[0])
            return

        context.user_data[PENDING_LOCATIONS] = locations

        keyboard = []

        for index, location in enumerate(locations):
            description = location.name

            if location.region:
                description += f" - {location.region}"

            description += f" ({location.country})"

            keyboard.append(
                [
                    InlineKeyboardButton(
                        description,
                        callback_data=f"location:{index}",
                    )
                ]
            )

        await update.message.reply_text(
            f"He encontrado {len(locations)} ubicaciones para '{query}'. "
            "¿Cuál estás buscando?",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def _send_forecast(self, message, context, location):
        context.user_data[LAST_LOCATION] = location

        weather_provider = context.application.bot_data["weather_provider"]

        weather_data = await weather_provider.get_forecast(
            location.latitude,
            location.longitude,
            DEFAULT_FORECAST_HOURS,
        )

        location_timezone = ZoneInfo(weather_data.timezone)
        hourly = weather_data.hourly_weather[:SUMMARY_HOURS]

        first_hour = hourly[0]
        local_time = first_hour.timestamp.astimezone(location_timezone)

        lines = [
            f"🌤️ <b>{location.name}, {location.country}</b>",
            "",
            f"📅 {local_time.strftime('%d/%m/%Y')}",
            f"🌡️ Temperatura: <b>{first_hour.temperature:.1f} °C</b>",
            f"🤒 Sensación térmica: {first_hour.apparent_temperature:.1f} °C",
            f"🌧️ Probabilidad de precipitación: {first_hour.precipitation_probability:.0f} %",
            f"💧 Precipitación: {first_hour.precipitation:.1f} mm",
            f"☀️ Índice UV: {first_hour.uv_index:.1f}",
            "",
            "<b>Próximas horas</b>",
        ]

        for hour in hourly:
            local_hour = hour.timestamp.astimezone(location_timezone)

            lines.append(
                f"{local_hour.strftime('%H:%M')} | "
                f"{hour.temperature:.1f} °C | "
                f"🌧️ {hour.precipitation_probability:.0f} % | "
                f"UV {hour.uv_index:.1f}"
            )

        lines.extend(
            [
                "",
                "Consulta el pronóstico completo con /forecast.",
            ]
        )

        await message.reply_text(
            "\n".join(lines),
            parse_mode="HTML",
        )

    async def select_location(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        query = update.callback_query
        await query.answer()

        pending_locations = context.user_data.get(PENDING_LOCATIONS)

        if pending_locations is None:
            await query.edit_message_text(
                "Esta selección ya no está disponible. Realiza una nueva búsqueda."
            )
            return

        try:
            index = int(query.data.split(":", 1)[1])
            selected_location = pending_locations[index]
        except (ValueError, IndexError):
            await query.edit_message_text(
                "La selección no es válida. Realiza una nueva búsqueda."
            )
            context.user_data.pop(PENDING_LOCATIONS, None)
            return

        context.user_data.pop(PENDING_LOCATIONS, None)

        await query.edit_message_text(
            f"¡Perfecto! Has seleccionado:\n\n"
            f"📍 {selected_location.name}\n"
            f"🌍 {selected_location.region or 'Región desconocida'}\n"
            f"País: {selected_location.country}\n"
            f"Coordenadas: {selected_location.latitude}, "
            f"{selected_location.longitude}"
        )

        await self._send_forecast(
            query.message,
            context,
            selected_location,
        )

    async def forecast(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        location = context.user_data.get(LAST_LOCATION)

        if location is None:
            await update.message.reply_text(
                "Primero debes buscar una ubicación con /search."
            )
            return

        weather_provider = context.application.bot_data["weather_provider"]

        weather_data = await weather_provider.get_forecast(
            location.latitude,
            location.longitude,
            DEFAULT_FORECAST_HOURS,
        )

        timezone = ZoneInfo(weather_data.timezone)

        lines = [
            f"🌤️ <b>Pronóstico de {location.name}, {location.country}</b>",
            "",
        ]

        for hour in weather_data.hourly_weather:
            local_time = hour.timestamp.astimezone(timezone)

            lines.append(
                f"<b>{local_time.strftime('%d/%m %H:%M')}</b>\n"
                f"🌡️ Temperatura: {hour.temperature:.1f} °C\n"
                f"🤒 Sensación térmica: {hour.apparent_temperature:.1f} °C\n"
                f"🌧️ Probabilidad de precipitación: "
                f"{hour.precipitation_probability:.0f} %\n"
                f"💧 Precipitación: {hour.precipitation:.1f} mm\n"
                f"☀️ Índice UV: {hour.uv_index:.1f}\n"
            )

        await update.message.reply_text(
            "\n".join(lines),
            parse_mode="HTML",
        )

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        awaiting_query = context.user_data.pop(AWAITING_QUERY, None)
        pending_locations = context.user_data.pop(PENDING_LOCATIONS, None)

        if awaiting_query is None and pending_locations is None:
            await update.message.reply_text("No tienes ninguna búsqueda pendiente.")
            return

        await update.message.reply_text(
            "Búsqueda cancelada. Ya puedes realizar otra consulta."
        )

    def run(self):
        print("Bot iniciado correctamente...")

        if self.settings.environment == "development":
            self.application.run_polling()
            return

        self.application.run_webhook(
            listen="0.0.0.0",
            port=self.settings.port,
            webhook_url=self.settings.webhook_url,
            secret_token=self.settings.webhook_secret,
        )
