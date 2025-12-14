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
