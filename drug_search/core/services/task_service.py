import hashlib
import logging
from enum import Enum

from arq import ArqRedis

logger = logging.getLogger(__name__)


class ARQ_JOBS(str, Enum):
    CREATE_DRUG = "create_drug_and_notify"
    UPDATE_DRUG = "update_drug_and_notify"
    ...


class TaskService:
    def __init__(self, arq_pool: ArqRedis):
        self.arq_pool = arq_pool

    @staticmethod
    def generate_job_id(query: str) -> str:
        """Возвращает закодированную строку (приведенную к байтам)"""
        normalized: str = query.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()[:8]

    async def enqueue_drug_creation(
            self,
            user_telegram_id: str,
            drug_name: str
    ):
        job_id: str = self.generate_job_id(drug_name)  # один для всех задач с одним drug_name

        try:
            job = await self.arq_pool.enqueue_job(
                ARQ_JOBS.CREATE_DRUG,
                user_telegram_id,
                drug_name,
                _job_id=job_id,
                _expires=300  # minutes
            )
            return {
                "status": "queued",
                "job_id": job_id,
                "drug_name": drug_name,
                "message": "Задача поставлена в очередь!"
            }
        except Exception as ex:
            if "already exists" in str(ex):
                return {
                    "status": "already_queued",
                    "job_id": job_id,
                    "drug_name": drug_name,
                    "message": "Препарат уже создается или создан"
                }
            raise ex
