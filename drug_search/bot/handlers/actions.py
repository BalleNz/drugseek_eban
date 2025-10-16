import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, LinkPreviewOptions

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.bot.keyboards import WrongDrugFoundedCallback, drug_keyboard, DescribeTypes, buy_request_keyboard, \
    ArrowTypes
from drug_search.bot.keyboards.callbacks import DrugUpdateRequestCallback, BuyDrugRequestCallback, \
    AssistantQuestionContinue
from drug_search.bot.lexicon import MessageTemplates
from drug_search.bot.utils.format_message_text import DrugMessageFormatter
from drug_search.core.dependencies.cache_service_dep import cache_service
from drug_search.core.schemas import (BuyDrugResponse, BuyDrugStatuses, UpdateDrugResponse,
                                      UpdateDrugStatuses, UserSchema, DrugExistingResponse)

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.callback_query(DrugUpdateRequestCallback.filter())
async def drug_update(
        callback_query: CallbackQuery,
        callback_data: DrugUpdateRequestCallback,
        access_token: str,
        state: FSMContext,  # noqa
        api_client: DrugSearchAPIClient
):
    """Обработка обновления препарата"""
    api_response: UpdateDrugResponse = await api_client.update_drug(
        drug_id=callback_data.drug_id,
        access_token=access_token
    )

    match api_response.status:
        case UpdateDrugStatuses.DRUG_UPDATING:
            await callback_query.message.edit_text(
                text=MessageTemplates.DRUG_UPDATING
            )
        case UpdateDrugStatuses.NOT_ENOUGH_TOKENS:
            await callback_query.message.edit_text(
                text=MessageTemplates.NOT_ENOUGH_UPDATE_TOKENS
            )
        case UpdateDrugStatuses.NEED_PREMIUM:
            await callback_query.message.edit_text(
                text=MessageTemplates.NEED_SUBSCRIPTION_FOR_UPDATE
            )


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
                text=MessageTemplates.NOT_ENOUGH_CREATE_TOKENS
            )
        case BuyDrugStatuses.NEED_PREMIUM:
            await callback_query.message.edit_text(
                text=MessageTemplates.NEED_SUBSCRIPTION
            )
        case BuyDrugStatuses.DANGER:
            await callback_query.message.edit_text(
                text=MessageTemplates.DRUG_IS_BANNED
            )


@router.callback_query(WrongDrugFoundedCallback.filter())
async def wrong_drug_founded(
        callback_query: CallbackQuery,
        access_token: str,
        state: FSMContext,  # noqa
        callback_data: WrongDrugFoundedCallback,
        api_client: DrugSearchAPIClient
):
    user: UserSchema = await cache_service.get_user_profile(access_token, callback_query.from_user.id)
    await callback_query.message.edit_text(MessageTemplates.DRUG_MANUAL_SEARCHING)

    drug_response: DrugExistingResponse = await api_client.search_drug_without_trigrams(callback_data.drug_name_query, access_token)
    if drug_response.is_exist:
        if drug_response.is_allowed:
            message_text: str = DrugMessageFormatter.format_drug_briefly(drug_response.drug)
            await callback_query.message.edit_text(
                message_text,
                reply_markup=drug_keyboard(
                    drug_id=drug_response.drug.id,
                    describe_type=DescribeTypes.BRIEFLY,
                    user_subscribe_type=user.subscription_type,
                    drug_name=drug_response.drug.name,
                    drug_last_update=drug_response.drug.updated_at
                ),
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
        else:
            # [ предложить купить препарат ]
            await callback_query.message.edit_text(
                text=MessageTemplates.DRUG_BUY_REQUEST.format(
                    drug_name_ru=drug_response.drug_name_ru
                ),
                reply_markup=buy_request_keyboard(
                    drug_id=drug_response.drug.id if drug_response.drug else None,
                    drug_name=drug_response.drug_name,
                    danger_classification=drug_response.danger_classification
                ),
            )
    else:
        await callback_query.message.edit_text(MessageTemplates.DRUG_IS_NOT_EXIST)


@router.callback_query(AssistantQuestionContinue.filter(F.arrow == ArrowTypes.BACK))
async def assistant_question_back(
        callback_query: CallbackQuery,
        callback_data: AssistantQuestionContinue,
        state: FSMContext,  # noqa
        access_token: str,
        api_client: DrugSearchAPIClient
):
    """Продолжить список ответа ассистента, но без найденных препаратов"""
    await api_client.question_answer(
        access_token=access_token,
        user_telegram_id=str(callback_query.from_user.id),
        question=callback_data.question,
        message_id=str(callback_query.message.message_id),
    )


@router.callback_query(AssistantQuestionContinue.filter(F.arrow == ArrowTypes.FORWARD))
async def assistant_question_forward(
        callback_query: CallbackQuery,
        callback_data: AssistantQuestionContinue,
        state: FSMContext,  # noqa
        access_token: str,
        api_client: DrugSearchAPIClient
):
    """
    Вернуть следующий список препаратов
    """
    await api_client.question_answer_continue(
        access_token=access_token,
        user_telegram_id=str(callback_query.from_user.id),
        question=callback_data.question,
        message_id=str(callback_query.message.message_id),
    )
