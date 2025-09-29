import logging

from drug_search.core.dependencies.assistant_service_dep import get_assistant_service
from drug_search.core.dependencies.pubmed_service_dep import get_pubmed_service
from drug_search.core.dependencies.telegram_service_dep import get_telegram_service
from drug_search.core.services.drug_service import DrugService
from drug_search.core.services.telegram_service import TelegramService
from drug_search.infrastructure.database.engine import get_async_session
from drug_search.infrastructure.database.repository.drug_repo import DrugRepository

logger = logging.getLogger(__name__)


async def create_drug_and_notify(
        ctx,  # ARQ CONTEXT
        user_telegram_id: str,
        drug_name: str,
        user_query: str
):
    """
    Создание препарата и отправка уведомления через ARQ
    """
    try:
        async with get_async_session() as session:
            drug_service = DrugService(
                repo=DrugRepository(session),
                assistant_service=await get_assistant_service(),
                pubmed_service=get_pubmed_service()
            )
            telegram_service: TelegramService = get_telegram_service()

            drug = await drug_service.new_drug(drug_name)

            logger.info(f"Successfully created drug '{drug_name}' with ID: {drug.id}")

            await telegram_service.send_drug_created_notification(
                user_telegram_id=user_telegram_id,
                drug_name=drug_name,
            )

            logger.info(f"Notification sent to user {user_telegram_id} for drug {drug.id}")

            return {
                "status": "job finished",
                "drug_name": drug_name,
            }

    except Exception as ex:

        return {
            "status": "error",
            "error": str(ex),
            "drug_name": drug_name,
        }


async def startup(ctx):
    """Выполняется при запуске worker"""
    logger.info("ARQ Worker starting up...")


async def shutdown(ctx):
    """Выполняется при остановке worker"""
    logger.info("ARQ Worker shutting down...")
