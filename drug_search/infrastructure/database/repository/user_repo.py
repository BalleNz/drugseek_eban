import datetime
import logging
import uuid
from typing import Sequence

from sqlalchemy import select, text, update, case
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from drug_search.core.lexicon import SUBSCRIPTION_TYPES, TOKENS_LIMIT, SubscriptionPackage
from drug_search.core.schemas import (UserTelegramDataSchema, UserSchema, DrugBrieflySchema,
                                      AllowedDrugsInfoSchema, ReferralSchema)
from drug_search.infrastructure.database.models.user import AllowedDrugs, User, UserRequestLog, Referral
from drug_search.infrastructure.database.repository.base_repo import BaseRepository
from drug_search.core.utils.referrals_funcs import get_ref_level
from drug_search.core.lexicon import REFERRALS_REWARDS

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=User, session=session)

    async def __refresh_requests(self, user: User):
        """Обновляет дневные лимиты
        При создании юзера столбцы последнего обновления уже есть
        """
        user.tokens_last_refresh = datetime.datetime.now()

        match user.subscription_type:
            case SUBSCRIPTION_TYPES.DEFAULT:
                user.allowed_tokens = TOKENS_LIMIT.DEFAULT_TOKENS_LIMIT
            case SUBSCRIPTION_TYPES.LITE:
                user.allowed_tokens = TOKENS_LIMIT.LITE_TOKENS_LIMIT
            case SUBSCRIPTION_TYPES.PREMIUM:
                user.allowed_tokens = TOKENS_LIMIT.PREMIUM_TOKENS_LIMIT

        await self.session.commit()

    async def get_user_from_telegram_id(self, telegram_id: str) -> UserSchema | None:
        """Возвращает схему юзера с телеграм айди"""
        stmt = (
            select(User).where(
                User.telegram_id == telegram_id
            )
            .options(
                selectinload(User.allowed_drugs)
            )
        )
        result = await self.session.execute(stmt)
        user: User | None = result.scalar_one_or_none()

        if not user:
            return None

        return user.get_schema()

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

        # [ refresh tokens ]
        if user.subscription_type != SUBSCRIPTION_TYPES.DEFAULT:
            refresh_interval_days = TOKENS_LIMIT.get_days_interval_to_refresh_tokens(user.subscription_type)
            if (datetime.datetime.now() - user.tokens_last_refresh).days >= refresh_interval_days:
                await self.__refresh_requests(user)

        return user.get_schema()

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

    async def get_allowed_drugs_info(self, user_id: uuid.UUID) -> AllowedDrugsInfoSchema:
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
            ORDER BY LOWER(drugs.name_ru)
        """)
        result = await self.session.execute(stmt)
        allowed_drugs_rows = result.fetchall()

        allowed_drugs = []
        for row in allowed_drugs_rows:
            drug_briefly = DrugBrieflySchema(
                drug_id=row.id,
                drug_name_ru=row.name_ru
            )
            allowed_drugs.append(drug_briefly)

        return AllowedDrugsInfoSchema(
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

    async def increment_tokens(
            self,
            user_id: uuid.UUID,
            tokens_amount: int = 0,
    ) -> None:
        """Атомарно увеличивает количество токенов.

        :var tokens_amount: количество токенов на поиск препаратов
        """
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                additional_tokens=User.additional_tokens + tokens_amount,

                # в случае, если мы тратим запросы, а не добавляем
                # всегда один прибавляется вне зависимости от потраченных
                used_tokens=User.used_tokens + (1 if tokens_amount > 0 else 0)
            )
        )
        await self.session.commit()

    async def decrease_tokens(
            self,
            user_id: uuid.UUID,
            tokens_amount: int = 0,
    ) -> None:
        """Атомарно уменьшает количество токенов.

        :var tokens_amount: количество токенов на поиск препаратов
        """
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                additional_tokens=case(
                    (User.allowed_tokens >= tokens_amount, User.additional_tokens),
                    else_=User.additional_tokens - (tokens_amount - User.allowed_tokens)
                ),
                allowed_tokens=case(
                    (User.allowed_tokens >= tokens_amount, User.allowed_tokens - tokens_amount),
                    else_=0
                ),
                used_tokens=User.used_tokens + 1
            )
        )
        await self.session.commit()

    async def give_subscription(self, user_id: uuid.UUID, subscription_package: SubscriptionPackage):
        """
        Выдает или обновляет подписку
        """
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                subscription_type=subscription_package.subscription_type,
                subscription_end=datetime.datetime.now() + datetime.timedelta(days=subscription_package.duration),
            )
        )
        await self.session.commit()

    async def add_user_log_request(self, user_id: uuid.UUID, user_query: str) -> None:
        """
        Запись логов юзера (поиск препов / обращение в нейронку)
        """
        logger.info(f"User log: {user_query}")
        await self.session.execute(
            insert(UserRequestLog)
            .values(
                user_id=user_id,
                user_query=user_query,
            )
        )
        await self.session.commit()

    async def simple_mode_toggle(self, user_id: uuid.UUID) -> None:
        """Переключение упрощенного режима"""
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                simple_mode=case(
                    (User.simple_mode.is_(True), False),
                    else_=True
                ),
            )
        )
        await self.session.commit()

    # [ REFERRALS ]
    async def get_referrals(self, referrer_telegram_id: int) -> Sequence[ReferralSchema]:
        """Получить всех рефералов пользователя"""
        stmt = select(Referral).where(
            Referral.referrer_telegram_id == referrer_telegram_id
        )

        result = await self.session.execute(stmt)
        referrals = result.scalars().all()

        return [referral.get_schema() for referral in referrals]

    async def check_referral_exists(self, referral_telegram_id: str) -> bool:
        """Проверить, существует ли реферал с таким telegram_id"""
        stmt = select(Referral).where(
            Referral.referral_telegram_id == referral_telegram_id
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create_referral(
            self,
            referrer_user: UserSchema,
            referral_user: UserSchema,
    ) -> ReferralSchema:
        """Создать новую реферальную связь"""

        referrer_telegram_id = referrer_user.telegram_id
        referral_telegram_id = referral_user.telegram_id

        # не существует ли уже такая связь
        if not self.check_referral_exists(referral_telegram_id):
            raise ValueError(f"Реферал с telegram_id {referral_telegram_id} уже существует")

        if referrer_telegram_id == referral_telegram_id:
            raise ValueError("Пользователь не может пригласить самого себя")

        await self.update(referrer_user.id, referrals_count=referrer_user.referrals_count+1)

        # [ check level ]
        ref_count: int = referrer_user.referrals_count
        ref_level_before: int = get_ref_level(ref_count)

        ref_level_after: int = get_ref_level(ref_count+1)
        if ref_level_before < ref_level_after:
            new_tokens_count = REFERRALS_REWARDS[ref_level_after] + referrer_user.additional_tokens
            await self.update(referrer_user.id, additional_tokens=new_tokens_count)

        await self.update(referral_user.id, referred_by_telegram_id=referrer_telegram_id)

        referral = Referral(
            referrer_telegram_id=referrer_telegram_id,
            referral_telegram_id=referral_telegram_id
        )

        self.session.add(referral)
        await self.session.commit()

        return referral.get_schema()

    def __del__(self):
        logger.info("USER REPO IS COLLECTED BY GARBAGE COLLECTOR")
