import logging

from arq.connections import RedisSettings

from drug_search.core.arq_tasks import drug_create, drug_update, assistant_answer
from drug_search.config import config
from drug_search.infrastructure.loggerConfig import configure_logging


# Настройки ARQ worker
class WorkerSettings:
    # Функции которые может выполнять worker
    functions = [
        drug_create,
        drug_update,
        assistant_answer
    ]

    # Настройки Redis
    redis_settings = RedisSettings.from_dsn(config.ARQ_REDIS_URL)

    # Настройки worker
    queue_name = config.ARQ_REDIS_QUEUE
    max_jobs = config.ARQ_MAX_JOBS
    job_timeout = 600  # 10 минут timeout на задачу
    keep_result = 600  # Хранить результат 10 мин

    # [ Logger ]
    async def on_startup(self):
        """Вызывается при запуске worker"""
        configure_logging()
        logger = logging.getLogger(__name__)
        logger.info("ARQ worker started with logging configured")

    # Retry политика
    retry_jobs = True
    max_tries = 3
