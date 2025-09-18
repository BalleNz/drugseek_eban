from uuid import UUID

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.core.schemas import UserTelegramDataSchema, AllowedDrugsSchema, DrugSchema
from drug_search.core.services.redis_service import RedisService


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
        # Пытаемся получить из кэша
        cached_token = await self.redis_service.get_access_token(telegram_data.telegram_id)
        if cached_token:
            return cached_token

        # Если нет в кэше, запрашиваем из API
        access_token = await self.api_client.telegram_auth(
            telegram_user_data=telegram_data
        )

        # Сохраняем в кэш
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
    ) -> AllowedDrugsSchema:
        """Получение списка разрешенных лекарств с кэшированием"""
        # Пытаемся получить из кэша
        cached_data = await self.redis_service.get_allowed_drugs(telegram_id)
        if cached_data:
            return cached_data

        # Если нет в кэше, запрашиваем из API
        fresh_data = await self.api_client.get_allowed_drugs(access_token=access_token)

        # Сохраняем в кэш
        await self.redis_service.set_allowed_drugs(
            telegram_id,
            fresh_data,
            expiry
        )

        return fresh_data

    async def get_drug(
            self,
            access_token: str,
            telegram_id: str,
            drug_id: UUID,
            expiry: int = 86400
    ) -> DrugSchema:
        """Получение информации о лекарстве с кэшированием"""
        # Пытаемся получить из кэша
        cached_data = await self.redis_service.get_drug(telegram_id, drug_id)
        if cached_data:
            return cached_data

        # Если нет в кэше, запрашиваем из API
        fresh_data = await self.api_client.get_drug(
            drug_id=drug_id,
            access_token=access_token
        )

        # Сохраняем в кэш
        await self.redis_service.set_drug(
            telegram_id,
            drug_id,
            fresh_data,
            expiry
        )

        return fresh_data
