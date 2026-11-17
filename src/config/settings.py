import os

from dotenv import load_dotenv


class Settings:
    def __init__(self):
        load_dotenv()

        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
