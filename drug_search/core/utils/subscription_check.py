import asyncio

from aiogram import Bot
from aiogram.enums import ChatMemberStatus


async def is_user_subscribed(user_telegram_id: int | str, channel_username: str, bot: Bot) -> bool:
    """Проверка подписки на каналы"""
    try:
        if type(user_telegram_id) is int:
            user_telegram_id = str(user_telegram_id)

        member = await bot.get_chat_member(chat_id=f"@{channel_username}", user_id=user_telegram_id)

        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR]:
            return True
        else:
            return False
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False


async def check_subscription_with_retry(
        telegram_id: int | str,
        channel_username: str,
        bot,
        max_attempts: int = 15,
        check_interval: int = 2
) -> bool:
    """
    Асинхронно проверяет подписку с повторными попытками
    """
    for attempt in range(max_attempts):
        is_subscribed = await is_user_subscribed(
            telegram_id,
            channel_username,
            bot
        )

        if is_subscribed:
            return True

        if attempt < max_attempts - 1:  # Не ждем после последней попытки
            await asyncio.sleep(check_interval)

    return False
