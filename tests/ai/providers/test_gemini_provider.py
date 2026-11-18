import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.ai.providers.gemini_provider import GeminiProvider


def test_gemini_provider_generates_text(monkeypatch):
    generate_content = AsyncMock(
        return_value=SimpleNamespace(text="Análisis meteorológico")
    )
    async_client = SimpleNamespace(
        models=SimpleNamespace(generate_content=generate_content),
        aclose=AsyncMock(),
    )
    monkeypatch.setattr(
        "src.ai.providers.gemini_provider.genai.Client",
        lambda api_key: SimpleNamespace(aio=async_client),
    )

    provider = GeminiProvider("test-api-key", "gemini-3.8-flash")

    result = asyncio.run(provider.generate_text("Datos meteorológicos"))

    assert result == "Análisis meteorológico"
    generate_content.assert_awaited_once()
    assert generate_content.await_args.kwargs["model"] == "gemini-3.8-flash"
    assert generate_content.await_args.kwargs["contents"] == "Datos meteorológicos"


def test_gemini_provider_rejects_empty_response(monkeypatch):
    async_client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=AsyncMock(return_value=SimpleNamespace(text=" "))
        ),
        aclose=AsyncMock(),
    )
    monkeypatch.setattr(
        "src.ai.providers.gemini_provider.genai.Client",
        lambda api_key: SimpleNamespace(aio=async_client),
    )

    provider = GeminiProvider("test-api-key", "gemini-3.8-flash")

    with pytest.raises(RuntimeError, match="empty response"):
        asyncio.run(provider.generate_text("Datos meteorológicos"))


def test_gemini_provider_closes_async_client(monkeypatch):
    close = AsyncMock()
    async_client = SimpleNamespace(
        models=SimpleNamespace(generate_content=AsyncMock()),
        aclose=close,
    )
    monkeypatch.setattr(
        "src.ai.providers.gemini_provider.genai.Client",
        lambda api_key: SimpleNamespace(aio=async_client),
    )

    provider = GeminiProvider("test-api-key", "gemini-3.8-flash")

    asyncio.run(provider.close())

    close.assert_awaited_once()
