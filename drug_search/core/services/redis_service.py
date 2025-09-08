from enum import Enum
from typing import Union
from uuid import UUID

from redis.asyncio import Redis

from drug_search.bot.api_client.drug_search_api import get_api_client
from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
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

    async def get_access_token(
            self,
            telegram_data: UserTelegramDataSchema
    ) -> str:
        redis_key: str = f"auth_{telegram_data.telegram_id}"
        access_token: str = await self.redis.get(redis_key)
        if not access_token:
            access_token: str = await self.api_client.telegram_auth(telegram_user_data=telegram_data)
            await self.redis.set(redis_key, access_token)
        return access_token

    async def get_cached_or_fetch(
            self,
            cache_key: str,  # user:{user_id}:drug_describe:{drug_id} | user:{user_id}:allowed_drugs_info
            drug_id: UUID = None,
            expiry: int = 4000,  # seconds
    ):
        """
        Универсальная функция для получения данных из кэша или их загрузки.
        Здесь используется только одномерный массив (одна ячейка).
        """
        # TODO разделить на две функции (посоветоваться с дипсиком)
        # TODO брать ацес токен хз как  (с дипсиком посовет (дать ему весь код))
        cache: Union[AllowedDrugsSchema, DrugSchema, None] = None

        if CacheKeys.ALLOWED_DRUGS in cache_key:
            cache: AllowedDrugsSchema = AllowedDrugsSchema.model_validate(
                await self.redis.get(name=cache_key)
            )
            if not cache:
                cache: AllowedDrugsSchema = await self.api_client.get_allowed_drugs(access_token=access_token)

        elif CacheKeys.DRUG_DESCRIBE in cache_key:
            cache: DrugSchema = DrugSchema.model_validate(
                await self.redis.get(name=cache_key)
            )
            if not cache:
                cache: DrugSchema = await self.api_client.get_drug(drug_id=drug_id, access_token=access_token)

        await self.redis.set(cache_key, cache.model_dump_json(), ex=expiry)

        return cache


async def get_redis_client() -> RedisService:
    redis_url: str = config.REDIS_URL
    redis_service = RedisService(
        redis_client=Redis.from_url(url=redis_url),
        api_client=await get_api_client()
    )
    return redis_service
