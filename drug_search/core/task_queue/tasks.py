import asyncio
import logging
from typing import Any, Dict

from database.engine import get_async_session
from database.repository.drug_repo import DrugRepository
from dependencies.assistant_service_dep import get_assistant_service
from dependencies.pubmed_service_dep import get_pubmed_service
from dependencies.telegram_service_dep import get_telegram_service
from services.drug_service import DrugService
from services.telegram_service import TelegramService

logger = logging.getLogger(__name__)


async def create_drug_and_notify(
        ctx,
        user_id: int,
        drug_name: str,
        user_query: str
) -> Dict[str, Any]:
    """
    Создание препарата и отправка уведомления через ARQ
    """
    try:
        logger.info(f"Starting drug creation task for user {user_id}, drug: {drug_name}")

        async with get_async_session() as session:
            drug_service = DrugService(
                repo=DrugRepository(session),
                assistant_service=await get_assistant_service(),
                pubmed_service=get_pubmed_service()
            )
            telegram_service: TelegramService = get_telegram_service()

            # Проверяем существование препарата
            existing_drug = await drug_service.find_drug_by_query(drug_name)

            if existing_drug:
                logger.info(f"Drug {drug_name} already exists, ID: {existing_drug.id}")
                drug_id = existing_drug.id
            else:
                # Создаем новый препарат
                drug = await drug_service.new_drug(drug_name=drug_name)
                drug_id = drug.id
                logger.info(f"Created new drug {drug_name} with ID: {drug_id}")

            # Отправляем уведомление пользователю
            await telegram_service.send_drug_created_notification(
                user_id=user_id,
                drug_id=drug_id,
                drug_name=drug_name,
                original_query=user_query
            )

            logger.info(f"Successfully processed drug creation for user {user_id}")

            return {
                "status": "success",
                "drug_id": drug_id,
                "drug_name": drug_name,
                "user_id": user_id
            }

    except Exception as e:
        logger.error(f"Error in create_drug_and_notify task: {str(e)}", exc_info=True)
        raise


async def startup(ctx):
    """Выполняется при запуске воркера"""
    logger.info("ARQ worker starting up...")
    ctx['startup_time'] = asyncio.get_event_loop().time()


async def shutdown(ctx):
    """Выполняется при остановке воркера"""
    logger.info("ARQ worker shutting down...")
