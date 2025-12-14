import asyncio
import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup

logger = logging.getLogger(__name__)


async def send_delayed_message(
        bot: Bot,
        chat_id: int,
        delay_minutes: int,
        text: str,
        reply_markup: InlineKeyboardMarkup | None
):
    """Отправление сообщение с задержкой"""
    try:
        await asyncio.sleep(delay_minutes * 60)

        await bot.send_message(
            chat_id,
            text=text,
            reply_markup=reply_markup
        )

        logger.info(f"Отправлено отложенное сообщение юзеру {chat_id}")
    except:
        raise
