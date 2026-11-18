from src.config.logging_config import configure_logging
from src.config.settings import Settings
from src.telegram_bot.bot import TelegramBot


def main():
    settings = Settings()
    configure_logging(settings)

    telegram_bot = TelegramBot(settings)
    telegram_bot.run()


if __name__ == "__main__":
    main()
