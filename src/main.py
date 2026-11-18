import logging

from src.config.settings import Settings
from src.telegram_bot.bot import TelegramBot


def main():
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    telegram_bot = TelegramBot(settings)
    telegram_bot.run()


if __name__ == "__main__":
    main()
