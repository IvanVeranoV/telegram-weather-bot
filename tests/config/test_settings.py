
import pytest

from src.config.settings import Settings
from src.config.settings_error import SettingsError


@pytest.fixture
def disable_dotenv(monkeypatch):
    monkeypatch.setattr("src.config.settings.load_dotenv", lambda: None)


def test_settings_accepts_valid_environment(
    monkeypatch,
    disable_dotenv,
):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")

    settings = Settings()

    assert settings.environment == "development"
    assert settings.telegram_bot_token == "test-token"


def test_settings_rejects_invalid_environment(
    monkeypatch,
    disable_dotenv,
):
    monkeypatch.setenv("APP_ENV", "testing")

    with pytest.raises(SettingsError):
        Settings()


def test_settings_rejects_missing_environment(
    monkeypatch,
    disable_dotenv,
):
    monkeypatch.delenv("APP_ENV", raising=False)

    with pytest.raises(SettingsError):
        Settings()


@pytest.mark.parametrize(
    "environment",
    ["staging", "production"],
)
def test_settings_accepts_valid_webhook_configuration(
    monkeypatch,
    disable_dotenv,
    environment,
):
    monkeypatch.setenv("APP_ENV", environment)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("WEBHOOK_URL", "https://example.com")
    monkeypatch.setenv("WEBHOOK_SECRET", "test-secret")
    monkeypatch.setenv("PORT", "8080")

    settings = Settings()

    assert settings.environment == environment
    assert settings.webhook_url == "https://example.com"
    assert settings.webhook_secret == "test-secret"
    assert settings.port == 8080


@pytest.mark.parametrize(
    "missing_variable",
    ["WEBHOOK_URL", "WEBHOOK_SECRET", "PORT"],
)
def test_settings_rejects_missing_webhook_configuration(
    monkeypatch,
    disable_dotenv,
    missing_variable,
):
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("WEBHOOK_URL", "https://example.com")
    monkeypatch.setenv("WEBHOOK_SECRET", "test-secret")
    monkeypatch.setenv("PORT", "8080")
    monkeypatch.delenv(missing_variable)

    with pytest.raises(SettingsError):
        Settings()


@pytest.mark.parametrize(
    "port",
    ["invalid", "0", "65536", "-1"],
)
def test_settings_rejects_invalid_port(
    monkeypatch,
    disable_dotenv,
    port,
):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("WEBHOOK_URL", "https://example.com")
    monkeypatch.setenv("WEBHOOK_SECRET", "test-secret")
    monkeypatch.setenv("PORT", port)

    with pytest.raises(SettingsError):
        Settings()


def test_settings_does_not_require_webhook_configuration_in_development(
    monkeypatch,
    disable_dotenv,
):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.delenv("WEBHOOK_URL", raising=False)
    monkeypatch.delenv("WEBHOOK_SECRET", raising=False)
    monkeypatch.delenv("PORT", raising=False)

    settings = Settings()

    assert settings.webhook_url is None
    assert settings.webhook_secret is None
    assert settings.port is None
