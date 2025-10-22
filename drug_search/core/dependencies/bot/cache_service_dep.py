from drug_search.core.dependencies.bot.api_client_dep import get_api_client
from drug_search.core.dependencies.redis_service_dep import get_redis_service
from drug_search.core.services.cache_logic.cache_service import CacheService

cache_service = CacheService(
    redis_service=get_redis_service(),
    api_client=get_api_client()
)


async def get_cache_service() -> CacheService:
    """Возвращает синглтон объект"""
    return cache_service
