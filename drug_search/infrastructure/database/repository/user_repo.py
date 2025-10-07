import datetime
import logging
import uuid
from typing import Any, Sequence

from sqlalchemy import select, text, Row, RowMapping, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from drug_search.core.lexicon import (PREMIUM_SEARCH_DAY_LIMIT, DEFAULT_SEARCH_DAY_LIMIT,
                                      SUBSCRIBE_TYPES, DEFAULT_QUESTIONS_DAY_LIMIT, LITE_QUESTIONS_DAY_LIMIT,
                                      LITE_SEARCH_DAY_LIMIT, PREMIUM_QUESTIONS_DAY_LIMIT)
from drug_search.core.schemas import UserTelegramDataSchema, UserSchema, AllowedDrugsSchema, DrugBriefly
from drug_search.infrastructure.database.models.user import AllowedDrugs, User
from drug_search.infrastructure.database.repository.base_repo import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=User, session=session)

    async def __refresh_requests(self, user: User):
        """Обновляет дневные лимиты
        При создании юзера столбцы последнего обновления уже есть
        """
        user.requests_last_refresh = datetime.datetime.now()

        match user.subscription_type:
            case SUBSCRIBE_TYPES.DEFAULT:
                user.allowed_search_requests = DEFAULT_SEARCH_DAY_LIMIT
                user.allowed_question_requests = DEFAULT_QUESTIONS_DAY_LIMIT

            case SUBSCRIBE_TYPES.LITE:
                user.allowed_search_requests = LITE_SEARCH_DAY_LIMIT
                user.allowed_question_requests = LITE_QUESTIONS_DAY_LIMIT

            case SUBSCRIBE_TYPES.PREMIUM:
                user.allowed_search_requests = PREMIUM_SEARCH_DAY_LIMIT
                user.allowed_question_requests = PREMIUM_QUESTIONS_DAY_LIMIT

        await self.session.commit()

    async def get_user(self, user_id: uuid.UUID) -> UserSchema | None:
        """Возвращает модель юзер со всеми смежными таблицами"""
        stmt = (
            select(User).where(
                User.id == user_id
            )
            .options(
                selectinload(User.allowed_drugs)
            )
        )
        result = await self.session.execute(stmt)
        user: User | None = result.scalar_one_or_none()
        if not user:
            return None

        # refresh day limits
        if (datetime.datetime.now() - user.requests_last_refresh).days >= 1:
            await self.__refresh_requests(user)
        return user.get_schema

    async def get_or_create_from_telegram(self, telegram_user: UserTelegramDataSchema) -> UserSchema | None:
        """
        Возвращает модель пользователя по Telegram ID если существует.
        Если не существует, создает нового пользователя по схеме из Telegram Web App.
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

        result = await self.session.execute(stmt)
        user = result.scalar_one()
        await self.session.commit()
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

            await self.session.execute(stmt)
            await self.session.commit()

        except Exception as ex:
            logger.exception(f"Ошибка при разрешении препарата пользователю: {ex}")
            raise ex

    async def get_allowed_drug_names(self, user_id: uuid.UUID) -> Sequence[Row[Any] | RowMapping | Any]:
        """
        Возвращает список имен разрешенных препаратов для юзера.
        """
        stmt = text(f"""
            SELECT drugs.id, drugs.name_ru AS _drug_name
            FROM allowed_drugs
            JOIN drugs ON drugs.id = allowed_drugs.drug_id
            WHERE allowed_drugs.user_id = '{user_id}'
        """)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_allowed_drugs_info(self, user_id: uuid.UUID) -> AllowedDrugsSchema:
        """
        Возвращает информацию о разрешенных препаратах для юзера в формате AllowedDrugsSchema.
        """
        total_drugs_stmt = text("SELECT COUNT(*) FROM drugs")
        total_result = await self.session.execute(total_drugs_stmt)
        drugs_count = total_result.scalar()

        stmt = text(f"""
            SELECT drugs.id, drugs.name, drugs.name_ru
            FROM allowed_drugs
            JOIN drugs ON drugs.id = allowed_drugs.drug_id
            WHERE allowed_drugs.user_id = '{user_id}'
        """)
        result = await self.session.execute(stmt)
        allowed_drugs_rows = result.fetchall()

        allowed_drugs = []
        for row in allowed_drugs_rows:
            drug_briefly = DrugBriefly(
                drug_id=row.id,
                drug_name_ru=row.name_ru
            )
            allowed_drugs.append(drug_briefly)

        return AllowedDrugsSchema(
            drugs_count=drugs_count,
            allowed_drugs_count=len(allowed_drugs),
            allowed_drugs=allowed_drugs if allowed_drugs else None
        )

    async def update_user_description(self, description: str, user_id: uuid.UUID):
        stmt = text("""
            UPDATE users 
            SET description = :description,
                updated_at = NOW()
            WHERE id = :user_id
        """).bindparams(description=description, user_id=user_id)

        await self.session.execute(stmt)
        await self.session.commit()

    async def decrement_user_requests(self, user_id: uuid.UUID, amount: int = 1) -> None:
        """Atomically decrements user's allowed_requests counter."""
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                allowed_search_requests=User.allowed_search_requests - amount,
                # в случае, если мы тратим запросы, а не добавляем
                # всегда один прибавляется вне зависимости от потраченных
                used_requests=User.used_requests + (1 if amount > 0 else 0)
            )
        )
        await self.session.commit()

    # TODO
    async def add_user_log_request(self):
        ...

    def __del__(self):
        logger.info("USER REPO IS COLLECTED BY GARBAGE COLLECTOR")
