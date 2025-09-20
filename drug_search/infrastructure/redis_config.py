from redis.asyncio import ConnectionPool

# REDIS_URL = "redis://redis:6379"  # docker
REDIS_URL = "redis://localhost:6379"
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
