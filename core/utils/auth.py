from datetime import datetime
from datetime import timedelta, UTC
from uuid import UUID

from fastapi import HTTPException

from aiogram.utils.web_app import WebAppInitData
from aiogram.utils.web_app import safe_parse_webapp_init_data
from jose import jwt


from config import config
from schemas.user import UserTelegramDataSchema


async def verify_telegram_data(init_data: str) -> UserTelegramDataSchema:
    """
    Валидация данных Telegram WebApp с преобразованием в вашу схему
    """
    try:
        # 1. Безопасный парсинг данных через aiogram
        parsed_data: WebAppInitData = safe_parse_webapp_init_data(
            token=config.BOT_TOKEN,
            init_data=init_data
        )

        # 2. Преобразование в вашу схему
        return UserTelegramDataSchema(
            telegram_id=str(parsed_data.user.id),
            first_name=parsed_data.user.first_name,
            last_name=parsed_data.user.last_name,
            username=parsed_data.user.username,
            auth_date=parsed_data.auth_date
        )
    except (ValueError, AttributeError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Telegram data: {str(e)}"
        )


async def generate_jwt(user_id: UUID, user_tg_id: int) -> str:
    """Генерация JWT токена"""
    return jwt.encode(
        {
            "sub": str(user_id),
            "tg_id": user_tg_id,
            "exp": datetime.now(UTC) + timedelta(days=30)
        },
        config.SECRET_KEY,
        algorithm="HS256"
    )
