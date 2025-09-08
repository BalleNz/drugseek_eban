from enum import Enum
from uuid import UUID

from redis.asyncio import Redis

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient


class CacheKeys(str, Enum):
    ALLOWED_DRUGS = "allowed_drugs_info"
    DRUG_DESCRIBE = "drug_describe"


class RedisService():
    def __init__(self, redis_client: Redis, api_client: DrugSearchAPIClient):
        self.redis = redis_client
        self.api_client = api_client

    async def get_cached_or_fetch(
            self,
            cache_key: str,
            drug_id: UUID,
            access_token: str,
            expiry: int = 4000,  # seconds
    ):
        """
        Универсальная функция для получения данных из кэша или их загрузки.
        """
        cache = await self.redis.lrange(name=cache_key, start=0, end=-1)

        if not cache:
            if cache_key == CacheKeys.ALLOWED_DRUGS:
                await self.api_client.get_allowed_drugs(access_token=access_token)
            elif cache_key == CacheKeys.DRUG_DESCRIBE:
                await self.api_client.get_drug(drug_id=drug_id, access_token=access_token)
            # TODO: получить кэш по ключу и сохранить

            fresh_data = ...
            await self.redis.set(cache_key, fresh_data, ex=expiry)

            return fresh_data

        return cache

# TODO подумать сделать DI вместо синглтона (как лучше спросить у дипсик)
redis_service = RedisService(redis_client=None)
