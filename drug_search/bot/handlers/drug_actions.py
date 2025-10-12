import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.bot.keyboards.callbacks import DrugUpdateCallback, BuyDrugRequestCallback
from drug_search.bot.lexicon import MessageTemplates
from drug_search.core.schemas import BuyDrugResponse, BuyDrugStatuses

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.callback_query(DrugUpdateCallback.filter())
async def assistant_request(
        callback_query: CallbackQuery,
        access_token: str,
        state: FSMContext,  # noqa
        api_client: DrugSearchAPIClient
):
    pass  # TODO


@router.callback_query(BuyDrugRequestCallback.filter())
async def drug_buy_request(
    callback_query: CallbackQuery,
    callback_data: BuyDrugRequestCallback,
    access_token: str,
    state: FSMContext,  # noqa
    api_client: DrugSearchAPIClient
):
    """Обработка покупки препарата"""
    api_response: BuyDrugResponse = await api_client.buy_drug(
        callback_data.drug_name,
        callback_data.drug_id,
        callback_data.danger_classification,
        access_token=access_token
    )

    match api_response.status:
        case BuyDrugStatuses.DRUG_CREATED:
            await callback_query.message.edit_text(
                text=MessageTemplates.DRUG_BUY_CREATED
            )
        case BuyDrugStatuses.DRUG_ALLOWED:
            await callback_query.message.edit_text(
                text=MessageTemplates.DRUG_BUY_ALLOWED.format(drug_name=api_response.drug_name)
            )
        case BuyDrugStatuses.NOT_ENOUGH_TOKENS:
            await callback_query.message.edit_text(
                text=MessageTemplates.NOT_ENOUGH_SEARCH_TOKENS
            )
        case BuyDrugStatuses.NEED_PREMIUM:
            await callback_query.message.edit_text(
                text=MessageTemplates.NEED_SUBSCRIPTION
            )
        case BuyDrugStatuses.DANGER:
            await callback_query.message.edit_text(
                text=MessageTemplates.DRUG_IS_BANNED
            )
