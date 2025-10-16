import logging
import uuid
from enum import Enum

from drug_search.bot.keyboards import ArrowTypes
from drug_search.core.dependencies.containers.service_container import get_service_container
from drug_search.core.schemas import DrugSchema, QuestionAssistantResponse
from drug_search.core.services.assistant_service import AssistantService
from drug_search.core.services.drug_service import DrugService
from drug_search.core.services.redis_service import RedisService
from drug_search.core.services.telegram_service import TelegramService
from drug_search.core.services.user_service import UserService

logger = logging.getLogger(__name__)


class AssistantOperations(str, Enum):
    QUESTION_REQUEST = "question"


async def drug_create(
        ctx,  # noqa
        drug_name: str,
        user_telegram_id: str,
        user_id: uuid.UUID
):
    """Логика создания препарата"""
    async with get_service_container() as container:
        # [ Dependencies ]
        drug_service: DrugService = await container.get_drug_service()
        telegram_service: TelegramService = await container.telegram_service
        user_service: UserService = await container.get_user_service()

        drug: DrugSchema = await drug_service.new_drug(drug_name)
        logger.info(f"Successfully created drug '{drug_name}' with ID: {drug.id}")
        await telegram_service.send_drug_created_notification(
            user_telegram_id=user_telegram_id,
            drug=drug,
        )
        await user_service.allow_drug_to_user(user_id=user_id, drug_id=drug.id)


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

        drug: DrugSchema = await drug_service.update_drug(drug_id=drug_id)

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
        old_message_id: str
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
            await redis_service.set_assistant_used_drugs(
                question=question_key,
                used_drugs=', '.join([drug.drug_name for drug in question_response.drugs])
            )

        await telegram_service.edit_message_with_assistant_answer(
            question_response=question_response,
            user_telegram_id=user_telegram_id,
            old_message_id=old_message_id,
            question=question_key,
            arrow=ArrowTypes.FORWARD
        )


async def assistant_answer_continue(
        ctx,  # noqa
        user_telegram_id: str,
        question: str,
        old_message_id: str,
):
    """
    Продолжение ответа на вопрос.
    """
    logger.info(f"Question: {question} for user {user_telegram_id}")

    question_key: str = question[:15]  # to safe callback data length

    async with get_service_container() as container:
        assistant_service: AssistantService = await container.assistant_service
        telegram_service: TelegramService = await container.telegram_service
        redis_service: RedisService = await container.redis_service

        question_response: QuestionAssistantResponse | None = await redis_service.get_assistant_answer_continue(
            question=question
        )
        if not question_response:
            old_drugs_name: str | None = await redis_service.get_assistant_used_drugs(question)
            if not old_drugs_name:
                await telegram_service.edit_message(
                    old_message_id,
                    user_telegram_id,
                    "К сожалению, сообщение потеряно."
                )
                return
            logger.info(f"new question. old drugs: {old_drugs_name}")

            question_response: QuestionAssistantResponse = await assistant_service.actions.answer_to_question_continue(
                question,
                old_drugs_name=old_drugs_name
            )
            logger.info(f"response: {question_response.model_dump_json()}")

            await redis_service.set_assistant_answer_continue(
                assistant_response=question_response,
                question=question_key,
            )

        await telegram_service.edit_message_with_assistant_answer(
            question_response=question_response,
            user_telegram_id=user_telegram_id,
            old_message_id=old_message_id,
            question=question_key,
            arrow=ArrowTypes.BACK
        )
