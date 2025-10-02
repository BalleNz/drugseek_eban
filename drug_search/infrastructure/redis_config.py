from typing import Final

from redis.asyncio import ConnectionPool

from drug_search.config import config


REDIS_URL: Final[str] = config.REDIS_URL

REDIS_POOL = ConnectionPool.from_url(
    REDIS_URL,
    max_connections=50,  # pool size
    decode_responses=True,

    # Таймауты
    socket_timeout=10,           # Таймаут операций
    socket_connect_timeout=10,   # Таймаут подключения
    socket_keepalive=True,

    # Кодировка
    encoding="utf-8",
    encoding_errors="strict",
)
