from arq.connections import RedisSettings

from arq import create_pool
from fastapi import Depends

from drug_search.config import config

from drug_search.core.services.tasks_logic.task_service import TaskService


async def get_arq_pool():
    """Создает и возвращает ARQ пул"""
    return await create_pool(RedisSettings.from_dsn(config.ARQ_REDIS_URL))


async def get_task_service(arq_pool = Depends(get_arq_pool)) -> TaskService:
    """Возвращает TaskService с инжекцией ARQ пула"""
    return TaskService(arq_pool)
