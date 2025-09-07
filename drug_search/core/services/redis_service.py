from redis.asyncio import Redis


class RedisService():
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def get_cached_or_fetch(
            self,
            cache_key: str,
            expiry: int = 4000  # seconds
    ):
        """
        Универсальная функция для получения данных из кэша или их загрузки.
        """
        cache = await self.redis.lrange(name=cache_key, start=0, end=-1)
        if not cache:
            # TODO: получить кэш по ключу и сохранить
            fresh_data = ...
            await self.redis.set(cache_key, fresh_data, ex=expiry)
            return fresh_data
        return cache

redis_service = RedisService(redis_client=None)
