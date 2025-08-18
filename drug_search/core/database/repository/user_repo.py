import logging
import uuid
from typing import Optional, Any, Sequence, AsyncGenerator

from fastapi import Depends
from sqlalchemy import select, text, Row, RowMapping, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from drug_search.core.database.engine import get_async_session
from drug_search.core.database.models.relationships import AllowedDrugs
from drug_search.core.database.models.user import User
from drug_search.core.database.repository.base_repo import BaseRepository
from drug_search.core.schemas import UserTelegramDataSchema, UserSchema

logger = logging.getLogger("bot.core.repository")


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=User, session=session)

    async def get_by_telegram_id(self, telegram_id: str) -> User | None:
        """
        Возвращает модель пользователя по телеграм айди.
        """
        stmt = (
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        result = await self._session.execute(stmt)
        user: Optional[User] = result.scalar_one_or_none()
        if not user:
            return None
        return user

    async def get_or_create_from_telegram(self, telegram_user: UserTelegramDataSchema) -> UserSchema | None:
        """
        Возвращает модель пользователя по Telegram ID если существует.
        Если не существует, Создает нового пользователя по схеме из Telegram Web App.
        """
        stmt = insert(User).values(
            telegram_id=telegram_user.telegram_id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name
        ).on_conflict_do_update(
            index_elements=['telegram_id'],
            set_={
                'username': telegram_user.username,
                'first_name': telegram_user.first_name,
                'last_name': telegram_user.last_name
            }
        ).returning(User)

        result = await self._session.execute(stmt)
        user = result.scalar_one()
        await self._session.commit()
        return UserSchema.model_validate(user.__dict__)

    async def allow_drug_to_user(self, drug_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """
        Разрешает препарат пользователю для его использования.
        """
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

    async def get_allowed_drug_names(self, user_id: uuid.UUID) -> Sequence[Row[Any] | RowMapping | Any]:
        """
        Возвращает список имен разрешенных препаратов для юзера.
        """
        stmt = text(f"""
            SELECT drugs.name_ru AS _drug_name
            FROM allowed_drugs
            JOIN drugs ON drugs.id = allowed_drugs.drug_id
            WHERE allowed_drugs.user_id = '{user_id}'
        """)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_allowed_drug_ids(self, user_id: uuid.UUID) -> Sequence[uuid.UUID]:
        """
        Возвращает список ID препаратов разрешенных для использования пользователю по user_id.
        """
        stmt = text(f"""
            SELECT allowed_drugs.drug_id
            FROM allowed_drugs
            JOIN drugs ON drugs.id = allowed_drugs.drug_id
            WHERE allowed_drugs.user_id = '{user_id}'
        """)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def update_user_description(self, description: str, user_id: uuid.UUID):
        stmt = text("""
            UPDATE users 
            SET description = :description,
                updated_at = NOW()
            WHERE id = :user_id
        """).bindparams(description=description, user_id=user_id)

        await self._session.execute(stmt)
        await self._session.commit()

    async def decrement_user_requests(self, user_id: uuid.UUID, amount: int = 1) -> None:
        """Atomically decrements user's allowed_requests counter."""
        await self._session.execute(
            update(User)
            .where(User.id == user_id)
            .values(allowed_requests=User.allowed_requests - amount)
        )
        await self._session.commit()

    # TODO
    async def add_user_log_request(self):
        ...

    def __del__(self):
        logger.info("USER REPO IS COLLECTED BY GARBAGE COLLECTOR")


async def get_user_repository(
        session_generator: AsyncGenerator[AsyncSession, None] = Depends(get_async_session)
) -> UserRepository:
    """
    :return: UserRepository obj with AsyncSession for onion service layer
    """
    async with session_generator as session:
        return UserRepository(session=session)
