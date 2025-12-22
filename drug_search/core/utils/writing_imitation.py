import asyncio
import logging
from contextlib import asynccontextmanager

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramAPIError

logger = logging.getLogger(__name__)

@asynccontextmanager
async def bot_typing_imitation(chat_id: int, bot: Bot):
    """Контекстный менеджер для имитации печати"""
    typing_task = None
    cancelled = False

    async def keep_typing():
        nonlocal cancelled

        while not cancelled:
            try:
                await bot.send_chat_action(
                    chat_id=chat_id,
                    action="typing",
                    request_timeout=2
                )
                await asyncio.sleep(2)
            except asyncio.CancelledError:
                # Задача отменена - выходим
                cancelled = True
                raise
            except TelegramRetryAfter as e:
                # Если превышен лимит, ждем указанное время
                await asyncio.sleep(e.retry_after)
            except (TelegramAPIError, Exception) as e:
                # Другие ошибки - логируем и продолжаем цикл с задержкой
                logger.debug(f"Error sending chat action: {e}")
                await asyncio.sleep(2)

    try:
        typing_task = asyncio.create_task(keep_typing())
        yield
    finally:
        """при выходе из контекстного менеджера"""
        cancelled = True

        if typing_task:
            typing_task.cancel()
            try:
                await typing_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.debug(f"Error stopping typing task: {e}")
