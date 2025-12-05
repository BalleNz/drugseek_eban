import base64

from aiogram import Bot
from aiogram.enums import ChatMemberStatus

from drug_search.core.lexicon import REFERRALS_LEVELS


def get_ref_level(referrals_count: int):
    """Возвращает уровень от количества рефералов"""
    level = 0
    for lvl, min_count in REFERRALS_LEVELS.items():
        if referrals_count >= min_count:
            level = lvl
        else:
            break
    return level


def generate_referral_url(user_id: str, bot_username: str):
    # [ encode ]
    token_bytes = user_id.encode()
    token = base64.b64encode(token_bytes).decode()

    link = f"https://t.me/{bot_username}?start=ref_{token}"

    return link


def decode_referral_token(token: str) -> str | None:
    """
    Расшифровываем токен в user_id
    """
    try:
        # Добавляем недостающие = если нужно
        while len(token) % 4 != 0:
            token += "="

        # [ decode ]
        user_id_bytes = base64.b64decode(token)
        user_id = user_id_bytes.decode()
        return user_id

    except Exception:
        return None


# [ BONUSES ]
async def is_user_subscribed(user_telegram_id: int, channel_username: str, bot: Bot) -> bool:
    """Проверка подписки на каналы"""
    try:
        member = await bot.get_chat_member(chat_id=f"@{channel_username}", user_id=user_telegram_id)

        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR]:
            return True
        else:
            return False
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False
