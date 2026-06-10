import logging
import uuid
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from drug_search.core.lexicon import SUBSCRIPTION_TYPES, DRUG_CATEGORY
from drug_search.core.schemas import PaymentSchema
from drug_search.infrastructure.database.engine import get_async_session
from drug_search.infrastructure.database.models.payment import Payment
from drug_search.infrastructure.database.repository.base_repo import BaseRepository

logger = logging.getLogger(__name__)


class PaymentRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Payment, session=session)

    async def give_subscription(
            self,
            sub_type: SUBSCRIPTION_TYPES,
            sub_duration_days: int,
            user_telegram_id: str,

            # [ for logs ]
            package_key: str,
            payment_name: str,
            price: int
    ) -> PaymentSchema | None:
        """выдача подписки"""
        stmt = text("""
            UPDATE users 
            SET subscription_type = :sub_type,
                subscription_end = NOW() + INTERVAL '1 DAY' * :sub_duration_days,
                updated_at = NOW()
            WHERE telegram_id = :user_telegram_id
            RETURNING id
        """)

        result = await self.session.execute(
            stmt,
            {
                "sub_type": sub_type.value,
                "sub_duration_days": sub_duration_days,
                "user_telegram_id": user_telegram_id
            }
        )

        row = result.fetchone()
        if not row:
            logger.warning(f"User with telegram_id {user_telegram_id} not found")
            return None

        user_id = row[0]  # user_id

        await self.session.commit()

        # [ logs ]
        return await self.create_payment_log(
            package_key=package_key,
            payment_name=payment_name,
            price=price,
            user_id=user_id
        )

    async def give_tokens(
            self,
            tokens_count: int,
            user_telegram_id: str,

            # [ for logs ]
            package_key: str,
            payment_name: str,
            price: int
    ) -> PaymentSchema | None:
        """выдача токенов"""
        stmt = text("""
            UPDATE users 
            SET additional_tokens = additional_tokens + :tokens_count,
                updated_at = NOW()
            WHERE telegram_id = :user_telegram_id
            RETURNING id, telegram_id, additional_tokens, allowed_tokens
        """)

        result = await self.session.execute(
            stmt,
            {
                "tokens_count": tokens_count,
                "user_telegram_id": user_telegram_id
            }
        )

        await self.session.commit()

        row = result.fetchone()
        if not row:
            logger.warning(f"User with telegram_id {user_telegram_id} not found")
            return None

        user_id = row[0]

        # [ logs ]
        return await self.create_payment_log(
            package_key=package_key,
            payment_name=payment_name,
            price=price,
            user_id=user_id
        )

    async def create_payment_log(
            self,
            package_key: str,
            payment_name: str,
            price: int,
            user_id: uuid.UUID
    ) -> PaymentSchema:
        return await self.save_from_schema(
            PaymentSchema(
                user_id=user_id,
                package_key=package_key,
                payment_name=payment_name,
                price=price,
            )
        )

    async def give_drug_pack(
            self,
            category: DRUG_CATEGORY | None,
            user_telegram_id: str,
            package_key: str,
            payment_name: str,
            price: int,
            drug_ids: list[uuid.UUID],
    ) -> PaymentSchema | None:
        user_stmt = text("""
            SELECT id FROM users WHERE telegram_id = :user_telegram_id
        """)
        user_result = await self.session.execute(
            user_stmt,
            {"user_telegram_id": user_telegram_id},
        )
        user_row = user_result.fetchone()
        if not user_row:
            logger.warning(f"User with telegram_id {user_telegram_id} not found")
            return None

        user_id = user_row[0]

        if drug_ids:
            ids_array = ", ".join(f"'{drug_id}'::uuid" for drug_id in drug_ids)
            insert_stmt = text(f"""
                INSERT INTO allowed_drugs (id, user_id, drug_id)
                SELECT gen_random_uuid(), :user_id, drug_id
                FROM unnest(ARRAY[{ids_array}]) AS drug_id
                WHERE NOT EXISTS (
                    SELECT 1 FROM allowed_drugs ad
                    WHERE ad.user_id = :user_id AND ad.drug_id = drug_id
                )
            """)
            await self.session.execute(insert_stmt, {"user_id": user_id})

        if category == DRUG_CATEGORY.PROHIBITED or category is None:
            premium_stmt = text("""
                UPDATE users
                SET subscription_type = :sub_type,
                    subscription_end = GREATEST(COALESCE(subscription_end, NOW()), NOW()) + INTERVAL '30 days',
                    updated_at = NOW()
                WHERE telegram_id = :user_telegram_id
            """)
            await self.session.execute(
                premium_stmt,
                {
                    "sub_type": SUBSCRIPTION_TYPES.PREMIUM.value,
                    "user_telegram_id": user_telegram_id,
                },
            )

        await self.session.commit()

        return await self.create_payment_log(
            package_key=package_key,
            payment_name=payment_name,
            price=price,
            user_id=user_id,
        )


async def get_payment_repo(
        session_generator: AsyncGenerator[AsyncSession, None] = Depends(get_async_session)
) -> PaymentRepository:
    async with session_generator as session:
        return PaymentRepository(session=session)
