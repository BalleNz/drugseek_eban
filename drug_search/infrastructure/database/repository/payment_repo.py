import logging
import uuid
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from drug_search.core.lexicon import SUBSCRIPTION_TYPES
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


async def get_payment_repo(
        session_generator: AsyncGenerator[AsyncSession, None] = Depends(get_async_session)
) -> PaymentRepository:
    async with session_generator as session:
        return PaymentRepository(session=session)
