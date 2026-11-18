class WeatherProviderError(Exception):
    """Raised when a weather provider returns invalid or inconsistent data."""


class WeatherRateLimitError(WeatherProviderError):
    """Raised when the weather provider rate limit is exceeded."""

    def __init__(self, retry_after: int | None = None):
        super().__init__()
        self.retry_after = retry_after


class WeatherTimeoutError(WeatherProviderError):
    """Raised when a weather provider request times out."""


class WeatherConnectionError(WeatherProviderError):
    """Raised when a connection to the weather provider cannot be established."""


class WeatherServiceUnavailableError(WeatherProviderError):
    """Raised when the weather provider is temporarily unavailable (HTTP 503)."""
