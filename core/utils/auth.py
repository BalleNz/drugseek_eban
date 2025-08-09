from datetime import datetime
from datetime import timedelta, UTC
from uuid import UUID

from jose import jwt

from config import config


async def generate_jwt(user_id: UUID, user_tg_id: str) -> str:
    """Генерация JWT-токена. Возращает JWT-токен"""
    return jwt.encode(
        {
            "sub": str(user_id),
            "tg_id": user_tg_id,
            "exp": datetime.now(UTC) + timedelta(days=30)
        },
        config.SECRET_KEY,
        algorithm="HS256"
    )
