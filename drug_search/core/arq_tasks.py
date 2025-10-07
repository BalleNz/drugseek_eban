import logging
import uuid
from contextlib import asynccontextmanager

from database.repository.user_repo import UserRepository
from dependencies.redis_service_dep import get_redis
from drug_search.core.dependencies.assistant_service_dep import get_assistant_service
from drug_search.core.dependencies.pubmed_service_dep import get_pubmed_service
from drug_search.core.dependencies.telegram_service_dep import get_telegram_service
from drug_search.core.schemas import DrugSchema
from drug_search.core.services.assistant_service import AssistantService
from drug_search.core.services.drug_service import DrugService
from drug_search.core.services.pubmed_service import PubmedService
from drug_search.core.services.telegram_service import TelegramService
from drug_search.core.services.user_service import UserService
from drug_search.infrastructure.database.engine import get_async_session
from drug_search.infrastructure.database.repository.drug_repo import DrugRepository
from services.redis_service import RedisService

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
        user_id: uuid.UUID,
        drug_name: str,  # ДВ
):
    """
    Создание препарата и отправка уведомления через ARQ
    """
    ctx['log'] = logger

    try:
        async with get_session() as session:
            assistant_service: AssistantService = await get_assistant_service()
            pubmed_service: PubmedService = await get_pubmed_service()
            telegram_service: TelegramService = await get_telegram_service()

            user_service: UserService = UserService(
                repo=UserRepository(session)
            )

            drug_service = DrugService(
                repo=DrugRepository(session),
                assistant_service=assistant_service,
                pubmed_service=pubmed_service
            )

            redis_service: RedisService = get_redis()
            await redis_service.invalidate_user_data(user_telegram_id)

            drug: DrugSchema = await drug_service.new_drug(drug_name)

            logger.info(f"Successfully created drug '{drug_name}' with ID: {drug.id}")

            await telegram_service.send_drug_created_notification(
                user_telegram_id=user_telegram_id,
                drug=drug,
            )

            await user_service.allow_drug_to_user(user_id=user_id, drug_id=drug.id)

            logger.info(f"Notification sent to user {user_telegram_id} for drug {drug.name}")

    except Exception as ex:
        logger.error(f"Exception while creating drug {drug_name}: {str(ex)}")
