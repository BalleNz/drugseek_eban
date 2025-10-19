import logging

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.core.lexicon import MailingStatuses
from drug_search.bot.lexicon import MessageTemplates

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.message(Command("mailing"))
async def mailing(
        message: Message,
        command: CommandObject,  # получаем объект команды
        access_token: str,
        api_client: DrugSearchAPIClient,
        state: FSMContext,  # noqa
):
    api_response: dict = await api_client.mailing(
        message=command.args,
        access_token=access_token
    )

    match api_response["status"]:
        case MailingStatuses.ONLY_FOR_ADMINS:
            await message.answer(
                MessageTemplates.ONLY_FOR_ADMINS
            )

        case MailingStatuses.SUCCESS:
            await message.answer(
                MessageTemplates.SUCCESS_MAILING
            )
