import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.bot.keyboards.callbacks import DrugActionsCallback, DrugActions

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.callback_query(DrugActionsCallback.filter(F.action == DrugActions.UPDATE_DRUG))
async def assistant_request(
        callback_query: CallbackQuery,
        access_token: str,
        state: FSMContext,
        api_client: DrugSearchAPIClient
):
    pass  # TODO
