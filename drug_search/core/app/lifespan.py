# app/lifespan.py
from contextlib import asynccontextmanager
from redis.asyncio import ConnectionPool
from redis.exceptions import RedisError

from drug_search.infrastructure.redis_config import REDIS_URL


@asynccontextmanager
async def lifespan(app):
    # Startup
    redis_pool = None
    try:
        redis_pool = ConnectionPool.from_url(
            REDIS_URL,
            max_connections=50,
            decode_responses=True,
            timeout=5,
            retry_on_timeout=True
        )
        # Проверяем соединение
        async with redis_pool.get_connection() as conn:
            await conn.send_command("PING")

        print("✅ Redis pool connected successfully")
        app.state.redis_pool = redis_pool
        yield

    except RedisError as e:
        print(f"❌ Redis connection failed: {e}")
        # Можно продолжить без Redis, если это допустимо
        app.state.redis_pool = None
        yield

    finally:
        # Shutdown
        if redis_pool:
            await redis_pool.disconnect()
            print("✅ Redis pool closed")
