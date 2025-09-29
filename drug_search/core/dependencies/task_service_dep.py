from arq.connections import RedisSettings

from arq import create_pool
from drug_search.config import config

from drug_search.core.services.task_service import TaskService

arq_pool = create_pool(RedisSettings.from_dsn(config.ARQ_REDIS_URL))
task_service: TaskService = TaskService(arq_pool)

async def get_task_service() -> TaskService:
    """singletone"""
    return task_service
