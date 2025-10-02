import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.types import Message

from api_client.drug_search_api import DrugSearchAPIClient

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.message
async def assistant_request(
        message: Message,
        access_token: str,
        state: FSMContext,
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

    messsage: SendMessage = message.answer(text="Запрос принят.. ожидайте")
    api_client

