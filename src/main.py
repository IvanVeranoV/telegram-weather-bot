from src.config.settings import Settings
from src.telegram_bot.bot import TelegramBot


def main():
    settings = Settings()
    telegram_bot = TelegramBot(settings)
    telegram_bot.run()


if __name__ == "__main__":
    main()
