import hashlib
import logging
import uuid
from enum import Enum

from arq import ArqRedis
from arq.jobs import Job, JobStatus

from drug_search.core.lexicon import ARROW_TYPES, JobStatuses

logger = logging.getLogger(__name__)


class ARQ_JOBS(str, Enum):
    """
    Функции из arq_tasks.py
    """
    DRUG_CREATE = "drug_create"
    DRUG_UPDATE = "drug_update"
    ASSISTANT_DRUGS_QUESTION = "assistant_drugs_question"
    ASSISTANT_QUESTION = "assistant_question"
    MAILING = "mailing"
    USER_DESCRIPTION_UPDATE = "user_description_update"


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
            user_id: uuid.UUID,
            drug_name: str,
    ) -> dict:
        job_id: str = self.generate_job_id(drug_name)

        job: Job = await self.arq_pool.enqueue_job(
            ARQ_JOBS.DRUG_CREATE.value,
            drug_name,
            user_telegram_id,
            user_id,
            _job_id=job_id,
            _expires=10
        )

        status: JobStatuses = JobStatuses.CREATED
        if job and await job.status() == JobStatus.in_progress:
            status = JobStatuses.QUEUED

        logger.info(f"Задача на создание препарата поставлена в очередь!")

        return {
            "status": status,
            "job_id": job_id,
            "drug_name": drug_name,
            "telegram_id": user_telegram_id
        }

    async def enqueue_drug_update(
            self,
            user_telegram_id: str,
            drug_id: uuid.UUID
    ) -> dict:
        job_id: str = self.generate_job_id(str(drug_id))

        job: Job = await self.arq_pool.enqueue_job(
            ARQ_JOBS.DRUG_UPDATE.value,
            user_telegram_id,
            drug_id,
            _job_id=job_id,
            _expires=10  # minutes
        )

        status: JobStatuses = JobStatuses.QUEUED
        if job and job.status() == JobStatus.in_progress:
            status = JobStatuses.CREATED

        logger.info(f"Задача на обновление препарата поставлена в очередь!")

        return {
            "status": status,
            "job_id": job_id,
            "drug_id": drug_id,
        }

    async def enqueue_assistant_question(
            self,
            user_telegram_id: str,
            question: str,
            old_message_id: str,
    ):
        """Задача не уникальная"""
        job: Job = await self.arq_pool.enqueue_job(
            ARQ_JOBS.ASSISTANT_QUESTION.value,
            user_telegram_id,
            question,
            old_message_id,
        )
        logger.info(f"Задача на вопрос ассистенту поставлена в очередь!")

        return {
            "status": f"{await job.status()}",
            "user_id": user_telegram_id,
            "question": question
        }

    async def enqueue_assistant_drugs_question(
            self,
            user_telegram_id: str,
            question: str,
            old_message_id: str,
            arrow: ARROW_TYPES
    ):
        """Задача не уникальная"""
        job: Job = await self.arq_pool.enqueue_job(
            ARQ_JOBS.ASSISTANT_DRUGS_QUESTION.value,
            user_telegram_id,
            question,
            old_message_id,
            arrow,
        )
        logger.info(f"Задача на вопрос ассистенту поставлена в очередь!")

        return {
            "status": f"{await job.status()}",
            "user_id": user_telegram_id,
            "question": question
        }

    async def enqueue_mailing(
            self,
            message: str
    ):
        job: Job = await self.arq_pool.enqueue_job(
            ARQ_JOBS.MAILING.value,
            message
        )
        logger.info(f"Задача на рассылку поставлена в очередь!")

        return {
            "status": str(await job.status()),
            "message": message
        }

    async def enqueue_user_description_update(
            self,
            user_id: uuid.UUID,
            user_telegram_id: str
    ):
        job: Job = await self.arq_pool.enqueue_job(
            ARQ_JOBS.USER_DESCRIPTION_UPDATE,
            user_id,
            user_telegram_id
        )
        logger.info(f"Задача на обновление описания юзера поставлена в очередь!")

        return {
            "status": str(await job.status())
        }
