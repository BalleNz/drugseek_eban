from redis.asyncio import Redis

from drug_search.core.services.redis_service import RedisService
from drug_search.infrastructure.redis_config import REDIS_POOL

redis_service = RedisService(
    redis_client=Redis(connection_pool=REDIS_POOL)
)


def get_redis() -> RedisService:
    return redis_service
