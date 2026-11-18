import logging


class SecretRedactionFilter(logging.Filter):
    """Redact configured secrets from log messages and exception traces."""

    def __init__(self, secrets: tuple[str | None, ...]):
        super().__init__()
        self.secrets = tuple(
            secret for secret in secrets if secret and len(secret) >= 8
        )
        self.formatter = logging.Formatter()

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()

        if record.exc_info:
            message += "\n" + self.formatter.formatException(record.exc_info)

        if record.stack_info:
            message += "\n" + record.stack_info

        for secret in self.secrets:
            message = message.replace(secret, "[REDACTED]")

        record.msg = message
        record.args = ()
        record.exc_info = None
        record.exc_text = None
        record.stack_info = None

        return True


def configure_logging(settings) -> None:
    """Configure application logging and redact configured credentials."""

    logging.basicConfig(level=logging.INFO)

    secrets = (
        settings.telegram_bot_token,
        settings.gemini_api_key,
        settings.webhook_secret,
    )

    redaction_filter = SecretRedactionFilter(secrets)

    for handler in logging.getLogger().handlers:
        handler.addFilter(redaction_filter)

    logging.getLogger("httpx").setLevel(logging.WARNING)
