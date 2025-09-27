from arq.connections import RedisSettings

from drug_search.config import config
from drug_search.core.task_queue import (
    create_drug_and_notify,
    send_bulk_notifications,
    startup,
    shutdown
)

# Настройки ARQ worker
class WorkerSettings:
    # Функции которые может выполнять worker
    functions = [
        create_drug_and_notify,
        send_bulk_notifications,
    ]

    # Настройки Redis
    redis_settings = RedisSettings.from_dsn(config.ARQ_REDIS_URL)

    # Настройки worker
    queue_name = config.ARQ_REDIS_QUEUE
    max_jobs = config.ARQ_MAX_JOBS
    job_timeout = 300  # 5 минут timeout на задачу
    keep_result = 3600  # Хранить результат 1 час

    # Хуки
    on_startup = startup
    on_shutdown = shutdown

    # Retry политика
    retry_jobs = True
    max_tries = 3
