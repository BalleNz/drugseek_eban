import hashlib
import logging
import uuid
from enum import Enum

from arq import ArqRedis

from arq_tasks import DrugOperations

logger = logging.getLogger(__name__)


class ARQ_JOBS(str, Enum):
    DRUG_OPERATIONS = "drug_operations"
    ...


class TaskService:
    def __init__(self, arq_pool: ArqRedis):
        self.arq_pool = arq_pool

    @staticmethod
    def generate_job_id(query: str) -> str:
        """Возвращает закодированную строку (приведенную к байтам)"""
        normalized: str = query.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()[:8]

    async def enqueue_drug_operations(
            self,
            operation: DrugOperations,
            user_telegram_id: str,
            user_id: uuid.UUID,
            drug_name: str
    ):
        job_id: str = self.generate_job_id(drug_name)  # один для всех задач с одним drug_name

        job = await self.arq_pool.enqueue_job(
            ARQ_JOBS.DRUG_OPERATIONS.value,
            operation,
            user_telegram_id,
            user_id,
            drug_name,
            _job_id=job_id,
            _expires=10  # minutes
        )
        if job:
            return {
                "status": "queued",
                "job_id": job.job_id,
                "drug_name": drug_name,
                "operation": operation,
                "message": "Задача поставлена в очередь!"
            }

        # TODO решить как будет отсылать уведомление, если другой человек уже создал задачу (в клиенте или здесь)
        return {
            "status": "already_queued",
            "job_id": job_id,
            "drug_name": drug_name,
            "operation": operation,
            "message": "Задача уже в очереди или выполнена."
        }
