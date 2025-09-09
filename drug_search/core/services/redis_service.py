from enum import Enum
from uuid import UUID

from redis.asyncio import Redis

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.bot.api_client.drug_search_api import get_api_client
from drug_search.config import config
from drug_search.core.schemas import DrugSchema, UserTelegramDataSchema
from drug_search.core.schemas.telegram_schemas import AllowedDrugsSchema


class CacheKeys(str, Enum):
    ALLOWED_DRUGS = "allowed_drugs_info"
    DRUG_DESCRIBE = "drug_describe"


class RedisService():
    def __init__(self, redis_client: Redis, api_client: DrugSearchAPIClient):
        self.redis = redis_client
        self.api_client = api_client

    @staticmethod
    def _get_token_key(telegram_id: str) -> str:
        return f"auth_{telegram_id}"

    @staticmethod
    def _get_allowed_drugs_key(telegram_id: str) -> str:
        return f"user:{telegram_id}:{CacheKeys.ALLOWED_DRUGS}"

    @staticmethod
    def _get_drug_describe_key(telegram_id: str, drug_id: UUID) -> str:
        return f"user:{telegram_id}:{CacheKeys.DRUG_DESCRIBE}:{drug_id}"

    async def get_or_refresh_access_token(
            self,
            telegram_data: UserTelegramDataSchema
    ) -> str:
        redis_key = self._get_token_key(telegram_data.telegram_id)
        access_token = await self.redis.get(redis_key)

        if not access_token:
            access_token = await self.api_client.telegram_auth(
                telegram_user_data=telegram_data
            )
            token_expire = config.ACCESS_TOKEN_EXPIRES_MINUTES
            await self.redis.set(redis_key, access_token, ex=token_expire)

        return access_token

    async def get_allowed_drugs(
            self,
            access_token: str,
            telegram_id: str,
            expiry: int = 86400  # 1 hour
    ) -> AllowedDrugsSchema:
        """Получение списка разрешенных лекарств с кэшированием"""
        cache_key = self._get_allowed_drugs_key(telegram_id)

        # Пытаемся получить из кэша
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return AllowedDrugsSchema.model_validate_json(cached_data)

        # Если нет в кэше, запрашиваем из API
        fresh_data = await self.api_client.get_allowed_drugs(access_token=access_token)

        # Сохраняем в кэш
        await self.redis.set(
            cache_key,
            fresh_data.model_dump_json(),
            ex=expiry
        )

        return fresh_data

    async def get_drug(
            self,
            access_token: str,
            telegram_id: str,
            drug_id: UUID,
            expiry: int = 86400  # 1 hour
    ) -> DrugSchema:
        """Получение информации о лекарстве с кэшированием"""
        cache_key = self._get_drug_describe_key(telegram_id, drug_id)

        # Пытаемся получить из кэша
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return DrugSchema.model_validate_json(cached_data)

        # Если нет в кэше, запрашиваем из API
        fresh_data = await self.api_client.get_drug(
            drug_id=drug_id,
            access_token=access_token
        )

        # Сохраняем в кэш
        await self.redis.set(
            cache_key,
            fresh_data.model_dump_json(),
            ex=expiry
        )

        return fresh_data

    async def invalidate_allowed_drugs(self, telegram_id: str) -> None:
        """Инвалидация кэша списка лекарств"""
        # TODO: добавить при покупке препарата юзером
        cache_key = self._get_allowed_drugs_key(telegram_id)
        await self.redis.delete(cache_key)

    async def invalidate_drug_describe(
        self, telegram_id: str, drug_id: UUID
    ) -> None:
        # TODO: добавить при обновлении данных об исследованиях
        """Инвалидация кэша информации о лекарстве"""
        cache_key = self._get_drug_describe_key(telegram_id, drug_id)
        await self.redis.delete(cache_key)


async def get_redis_client() -> RedisService:
    redis_url: str = config.REDIS_URL
    redis_service = RedisService(
        redis_client=Redis.from_url(url=redis_url),
        api_client=await get_api_client()
    )
    return redis_service
