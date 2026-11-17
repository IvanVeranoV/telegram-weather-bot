import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from src.telegram_bot.bot import AWAITING_QUERY, TelegramBot


def create_bot():
    return TelegramBot.__new__(TelegramBot)


def test_search_without_arguments_activates_awaiting_query():
    bot = create_bot()

    update = SimpleNamespace(message=SimpleNamespace(reply_text=AsyncMock()))

    context = SimpleNamespace(args=[], user_data={})

    asyncio.run(bot.search(update, context))

    assert context.user_data[AWAITING_QUERY] is True
    update.message.reply_text.assert_awaited_once_with("¿Qué ciudad quieres consultar?")


def test_handle_search_query_processes_city():
    bot = create_bot()

    update = SimpleNamespace(
        message=SimpleNamespace(text="Madrid", reply_text=AsyncMock())
    )

    geocoding_provider = SimpleNamespace(search=AsyncMock(return_value=[]))

    context = SimpleNamespace(
        user_data={AWAITING_QUERY: True},
        application=SimpleNamespace(
            bot_data={"geocoding_provider": geocoding_provider}
        ),
    )

    asyncio.run(bot.handle_search_query(update, context))

    geocoding_provider.search.assert_awaited_once_with("Madrid")
    assert AWAITING_QUERY not in context.user_data


def test_cancel_removes_awaiting_query():
    bot = create_bot()

    update = SimpleNamespace(message=SimpleNamespace(reply_text=AsyncMock()))

    context = SimpleNamespace(user_data={AWAITING_QUERY: True})

    asyncio.run(bot.cancel(update, context))

    assert AWAITING_QUERY not in context.user_data
    update.message.reply_text.assert_awaited_once()


def test_normal_message_without_search_is_ignored():
    bot = create_bot()

    update = SimpleNamespace(
        message=SimpleNamespace(text="Madrid", reply_text=AsyncMock())
    )

    context = SimpleNamespace(user_data={})

    asyncio.run(bot.handle_search_query(update, context))

    update.message.reply_text.assert_not_awaited()
