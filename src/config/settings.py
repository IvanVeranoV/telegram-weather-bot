import os

from dotenv import load_dotenv

from src.config.settings_error import SettingsError


class Settings:
    VALID_ENVIRONMENTS = frozenset(
        {
            "development",
            "staging",
            "production",
        }
    )

    WEBHOOK_ENVIRONMENTS = frozenset(
        {
            "staging",
            "production",
        }
    )

    def __init__(self):
        load_dotenv()

        self.environment = os.getenv("APP_ENV")

        if self.environment not in self.VALID_ENVIRONMENTS:
            raise SettingsError(f"Invalid APP_ENV value: {self.environment!r}")

        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

        self.webhook_url = None
        self.webhook_secret = None
        self.port = None

        if self.environment in self.WEBHOOK_ENVIRONMENTS:
            self.webhook_url = os.getenv("WEBHOOK_URL")
            self.webhook_secret = os.getenv("WEBHOOK_SECRET")
            port_value = os.getenv("PORT")

            if not self.webhook_url:
                raise SettingsError("WEBHOOK_URL is required")

            if not self.webhook_secret:
                raise SettingsError("WEBHOOK_SECRET is required")

            if not port_value:
                raise SettingsError("PORT is required")

            try:
                self.port = int(port_value)
            except ValueError as error:
                raise SettingsError("PORT must be an integer") from error

            if not 1 <= self.port <= 65535:
                raise SettingsError("PORT must be between 1 and 65535")
