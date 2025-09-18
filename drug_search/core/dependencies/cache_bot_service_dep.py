from dependencies.api_client_dep import get_api_client
from dependencies.redis_service_dep import get_redis
from drug_search.core.services.cache_bot_service import CacheService

cache_service = CacheService(
    redis_service=get_redis(),
    api_client=get_api_client()
)


async def get_cache_service() -> CacheService:
    """Возвращает синглтон объект"""
    return cache_service
