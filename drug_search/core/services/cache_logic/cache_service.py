import datetime
import logging
from typing import Optional
from uuid import UUID

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.core.schemas import UserTelegramDataSchema, DrugSchema, UserSchema, AllowedDrugsInfoSchema
from drug_search.core.services.cache_logic.redis_service import RedisService

logger = logging.getLogger(__name__)


class CacheService:
    """Сервис для работы с кэшем"""

    def __init__(
            self,
            redis_service: RedisService,
            api_client: DrugSearchAPIClient
    ):
        self.redis_service = redis_service
        self.api_client = api_client

    async def get_or_refresh_access_token(
            self,
            telegram_data: UserTelegramDataSchema
    ) -> str:
        """Получение или обновление access token"""
        cached_token: Optional[str] = await self.redis_service.get_access_token(telegram_data.telegram_id)
        if cached_token:
            return cached_token

        access_token = await self.api_client.telegram_auth(
            telegram_user_data=telegram_data
        )

        await self.redis_service.set_access_token(
            telegram_data.telegram_id,
            access_token
        )

        return access_token

    async def get_allowed_drugs(
            self,
            access_token: str,
            telegram_id: str,
            expiry: int = 86400
    ) -> AllowedDrugsInfoSchema:
        """Получение списка разрешенных лекарств с кэшированием"""
        cached_data: Optional[AllowedDrugsInfoSchema] = await self.redis_service.get_allowed_drugs(telegram_id)
        if cached_data:
            return cached_data

        fresh_data: AllowedDrugsInfoSchema = await self.api_client.get_allowed_drugs(access_token=access_token)

        await self.redis_service.set_allowed_drugs(
            telegram_id,
            fresh_data,
            expiry
        )

        return fresh_data

    async def get_drug(
            self,
            access_token: str,
            drug_id: UUID,
            expiry: int = 15  # временно для дебага
    ) -> DrugSchema:
        """Получение информации о лекарстве с кэшированием"""
        cached_data: Optional[DrugSchema] = await self.redis_service.get_drug(drug_id)
        if cached_data:
            logger.info(f"Cache: drug получен {cached_data.name} — {cached_data.id}")
            return cached_data

        fresh_data: DrugSchema = await self.api_client.get_drug(
            drug_id=drug_id,
            access_token=access_token
        )

        await self.redis_service.set_drug(
            drug_id,
            fresh_data,
            expiry
        )

        return fresh_data

    async def get_user_profile(
            self,
            access_token: str,
            telegram_id: str,
            expiry: int = 86400
    ) -> UserSchema:
        """Получение информации о юзере"""
        cache_data: Optional[UserSchema] = await self.redis_service.get_user_profile(telegram_id)
        if cache_data:
            if cache_data.subscription_end and (
                    not cache_data.subscription_end < datetime.datetime.now() and not cache_data.tokens_last_refresh < datetime.datetime.now()):
                return cache_data

        fresh_data: UserSchema = await self.api_client.get_current_user(access_token)

        await self.redis_service.set_user_profile(
            telegram_id,
            fresh_data,
            expiry
        )

        return fresh_data
