import asyncio
import logging
import time
import uuid
from typing import Sequence, Generator

from drug_search.core.dependencies.containers.service_container import get_service_container
from drug_search.core.lexicon import ADMINS_TG_ID, ARROW_TYPES
from drug_search.core.schemas import DrugSchema, QuestionAssistantResponse, UserSchema
from drug_search.core.services.assistant_service import AssistantService
from drug_search.core.services.cache_logic.redis_service import RedisService
from drug_search.core.services.models_service.drug_service import DrugService
from drug_search.core.services.models_service.user_service import UserService
from drug_search.core.services.telegram_service import TelegramService
from drug_search.infrastructure.database.repository.user_repo import UserRepository
from drug_search.bot.lexicon.enums import DrugMenu

logger = logging.getLogger(__name__)


async def drug_create(
        ctx,  # noqa
        drug_name: str,
        user_telegram_id: str,
        user_id: uuid.UUID,
):
    """Логика создания препарата"""
    async with get_service_container() as container:
        # [ Dependencies ]
        drug_service: DrugService = await container.get_drug_service()
        telegram_service: TelegramService = await container.telegram_service
        user_service: UserService = await container.get_user_service()
        redis_service: RedisService = await container.redis_service

        drug: DrugSchema = await drug_service.update_or_create_drug(drug_name)
        logger.info(f"Successfully created drug '{drug_name}' with ID: {drug.id}")

        await telegram_service.send_drug_created_notification(
            user_telegram_id=user_telegram_id,
            drug=drug,
        )

        await user_service.allow_drug_to_user(user_id=user_id, drug_id=drug.id)

        await redis_service.invalidate_user_data(user_telegram_id)


async def drug_update(
        ctx,  # noqa
        user_telegram_id: str,
        drug_id: uuid.UUID,
):
    """Логика обновления препарата"""
    ctx['log'] = logger

    async with get_service_container() as container:
        # [ Dependencies ]
        drug_service: DrugService = await container.get_drug_service()
        telegram_service: TelegramService = await container.telegram_service
        redis_service: RedisService = await container.redis_service

        drug: DrugSchema = await drug_service.repo.get(drug_id)

        drug = await drug_service.update_or_create_drug(drug_name=drug.name)

        # [ invalidate cache ]
        await redis_service.invalidate_drug(drug_id)

        # [ notification ]
        logger.info(f"Препарат {drug_id} обновлен для пользователя {user_telegram_id}")
        await telegram_service.send_drug_updated_notification(
            user_telegram_id=user_telegram_id,
            drug=drug
        )


async def assistant_answer(
        ctx,  # noqa
        user_telegram_id: str,
        question: str,
        old_message_id: str,
        arrow: ARROW_TYPES
):
    """
    Отправляется ответ от нейронки в телеграм.
    """
    logger.info(f"Question: {question} for user {user_telegram_id}")

    question_key: str = question[:15]  # to safe callback data length

    async with get_service_container() as container:
        assistant_service: AssistantService = await container.assistant_service
        telegram_service: TelegramService = await container.telegram_service
        redis_service: RedisService = await container.redis_service

        question_response: QuestionAssistantResponse | None = await redis_service.get_assistant_answer(
            question=question
        )
        if not question_response:
            question_response: QuestionAssistantResponse = await assistant_service.actions.answer_to_question(question)

            await redis_service.set_assistant_answer(
                assistant_response=question_response,
                question=question_key,
            )

        await telegram_service.edit_message_with_assistant_answer(
            question_response=question_response,
            user_telegram_id=user_telegram_id,
            old_message_id=old_message_id,
            question=question_key,
            arrow=arrow
        )


async def mailing(
        ctx,  # noqa
        message: str
):
    time_start: float = time.time()

    async with get_service_container() as container:
        # [ deps ]
        user_repo: UserRepository = await container.get_user_repo()
        telegram_service: TelegramService = await container.telegram_service

        # [ variables ]
        users: Sequence[UserSchema] = await user_repo.get_all()
        users_telegram_id: Generator[str] = (user.telegram_id for user in users)
        banned_users = 0

        # [ logic ]
        for i, user_telegram_id in enumerate(users_telegram_id):

            # каждые 30 сообщений задержка 1 сек
            if i % 30 == 0:
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.05)  # 50ms между обычными сообщениями

            try:
                await telegram_service.send_message(
                    user_telegram_id,
                    message=message
                )
            except ValueError:
                banned_users += 1

        message: str = f"""
        Отправка закончена.
        
        <b>Всего отправлено:</b> {users.__len__()}
        <b>Заблокировали бота:</b> {banned_users} человек
        
        <b>Прошло времени:</b> {time.time() - time_start:.2f} секунд.
        """

        for admin_id in ADMINS_TG_ID:
            await telegram_service.send_message(
                user_telegram_id=admin_id,
                message=message
            )


async def user_description_update(
        ctx,  # noqa
        user_id: uuid.UUID,
        user_tg_id: str,
):
    async with get_service_container() as container:
        user_service: UserService = await container.get_user_service_with_assistant()
        telegram_service: TelegramService = await container.telegram_service
        redis_service: RedisService = await container.redis_service

        await user_service.update_user_description(user_id)

        await redis_service.invalidate_user_data(user_tg_id)

        await telegram_service.send_user_description_updated(user_telegram_id=user_tg_id)
