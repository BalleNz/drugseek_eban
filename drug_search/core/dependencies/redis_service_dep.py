from redis.asyncio import Redis

from drug_search.core.services.cache_logic.redis_service import RedisService
from drug_search.infrastructure.redis_config import REDIS_POOL

redis_client = Redis(connection_pool=REDIS_POOL)

redis_service = RedisService(
    redis_client=redis_client
)


def get_redis_service() -> RedisService:
    return redis_service
