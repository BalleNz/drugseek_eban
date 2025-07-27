import logging
import uuid
from typing import Optional, Any, Coroutine

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import get_async_session
from database.models.relationships import AllowedDrugs
from database.models.user import User
from database.repository.base import BaseRepository
from sqlalchemy import select, insert

from schemas import UserTelegramDataSchema, UserSchema

logger = logging.getLogger("bot.core.repository")


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=User, session=session)

    async def get_by_telegram_id(self, telegram_id: str) -> User | None:
        """
        Возвращает модель пользователя по телеграм айди.
        """
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        user: Optional[User] = result.scalar_one_or_none()
        if not user:
            return None
        return user

    async def get_or_create_from_telegram(self, telegram_user: UserTelegramDataSchema) -> UserSchema | None:
        """
        Возвращает модель пользователя по Telegram ID если существует.

        Если не сущетсвует, Создает нового пользователя по схеме из Telegram Web App.
        """
        user: User = await self.get_by_telegram_id(telegram_user.telegram_id)
        if not user:
            user = User(
                telegram_id=telegram_user.telegram_id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
            )
            user = await self.create(user)

        return UserSchema.model_validate(user.__dict__)

    async def allow_drug_to_user(self, drug_id: uuid.UUID, user_id: uuid.UUID) -> None:
        try:
            stmt = insert(AllowedDrugs).values(
                user_id=user_id,
                drug_id=drug_id
            )

            await self._session.execute(stmt)
            await self._session.commit()

        except Exception as ex:
            logger.exception(f"Ошибка при разрешении препарата пользователю: {ex}")
            raise ex


def get_user_repository(session: AsyncSession = Depends(get_async_session)) -> UserRepository:
    """
    :return: UserRepository obj with AsyncSession for onion service layer
    """
    return UserRepository(session=session)
