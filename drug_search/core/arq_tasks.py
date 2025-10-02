import logging
from contextlib import asynccontextmanager

from drug_search.core.dependencies.assistant_service_dep import get_assistant_service
from drug_search.core.dependencies.pubmed_service_dep import get_pubmed_service
from drug_search.core.dependencies.telegram_service_dep import get_telegram_service
from drug_search.core.services.drug_service import DrugService
from drug_search.core.services.telegram_service import TelegramService
from drug_search.infrastructure.database.engine import get_async_session
from drug_search.infrastructure.database.repository.drug_repo import DrugRepository

logger = logging.getLogger(__name__)

@asynccontextmanager
async def get_session():  # TODO сделать так же в repo
    """Правильное использование асинхронного генератора сессии"""
    session_gen = get_async_session()
    session = await session_gen.__anext__()
    try:
        yield session
    finally:
        try:
            await session_gen.__anext__()
        except StopAsyncIteration:
            pass


async def create_drug_and_notify(
        ctx,  # ARQ CONTEXT
        user_telegram_id: str,
        drug_name: str,  # ДВ
):
    """
    Создание препарата и отправка уведомления через ARQ
    """
    ctx['log'] = logger

    try:
        async with get_session() as session:
            assistant_service = await get_assistant_service()
            pubmed_service = await get_pubmed_service()
            telegram_service = await get_telegram_service()

            drug_service = DrugService(
                repo=DrugRepository(session),
                assistant_service=assistant_service,
                pubmed_service=pubmed_service
            )

            drug = await drug_service.new_drug(drug_name)

            logger.info(f"Successfully created drug '{drug_name}' with ID: {drug.id}")

            await telegram_service.send_drug_created_notification(
                user_telegram_id=user_telegram_id,
                drug=drug,
            )

            logger.info(f"Notification sent to user {user_telegram_id} for drug {drug.id}")

    except Exception as ex:
        logger.error(f"Exception while creating drug {drug_name}: {str(ex)}")
