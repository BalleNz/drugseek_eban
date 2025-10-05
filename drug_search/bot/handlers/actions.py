import asyncio
import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, LinkPreviewOptions

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.bot.keyboards import DescribeTypes, drug_describe_types_keyboard
from drug_search.bot.utils.format_message_text import AssistantMessageFormatter, DrugMessageFormatter
from drug_search.core.lexicon.enums import ACTIONS_FROM_ASSISTANT
from drug_search.core.schemas import QuestionAssistantResponse, SelectActionResponse, DrugExistingResponse

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.message()
async def assistant_request(
        message: Message,
        access_token: str,
        state: FSMContext,  # TODO попробовать убрать функцию и удалить state
        api_client: DrugSearchAPIClient
):
    """ручка для возвращения ответа ассистента в виде:
    "response": {
        "action": "drug_search/question_from_user/spam",
        "drug_exist": bool | None,
        "drug_name": str | None,
        "answer": str | None,
        ""
    }
    """
    # TODO: делает задачу в TaskService

    # TODO в клиете обработку если не нужный препарат найден (дергаем ручку ассистента)

    drug_existing_response: DrugExistingResponse | None = await api_client.search_drug(message.text,
                                                                                       access_token=access_token)

    if drug_existing_response.is_exist:
        if drug_existing_response.is_drug_in_database:
            message_text = DrugMessageFormatter.format_drug_briefly(drug_existing_response.drug)
            await message.answer(
                message_text,
                reply_markup=drug_describe_types_keyboard(
                    drug_id=drug_existing_response.drug.id,
                    describe_type=DescribeTypes.BRIEFLY,
                ),
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
        else:
            await message.answer("такого препарат нет в БД ")
    else:
        message_request: Message = await message.answer(text="Запрос принят.. обрабатываю")

        asyncio.create_task(process_assistant_request(
            message, access_token, state, api_client, message_request
        ))


async def process_assistant_request(
        message: Message,
        access_token: str,
        state: FSMContext,
        api_client: DrugSearchAPIClient,
        message_request: Message
):
    # TODO поменять полностью логику:
    # СНАЧАЛА ПОИСК ПРЕПАРАТА
    # ЕСЛИ НЕ НАЙДЕН -> поиск действия (спам или вопрос (только два действия теперь))

    try:
        action_response: SelectActionResponse = await api_client.assistant_get_action(
            access_token, message.text
        )

        match action_response.action:
            case ACTIONS_FROM_ASSISTANT.QUESTION:
                answer_response: QuestionAssistantResponse = await api_client.assistant_get_answer(
                    access_token, message.text
                )
                message_text: str = AssistantMessageFormatter.format_assistant_answer(answer_response)
                await message_request.edit_text(message_text)

            case ACTIONS_FROM_ASSISTANT.DRUG_SEARCH:
                ...

            case ACTIONS_FROM_ASSISTANT.SPAM:
                await message.answer("Это сообщение распознано как спам")

            case ACTIONS_FROM_ASSISTANT.OTHER:
                await message.answer("Пожалуйста, уточните ваш запрос")

    except Exception as e:
        logger.error(f"Error processing assistant request: {e}")
        await message.answer("Произошла ошибка при обработке запроса")
