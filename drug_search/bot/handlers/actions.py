import logging
import uuid

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, LinkPreviewOptions, Message

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.bot.keyboards import WrongDrugFoundedCallback, drug_keyboard
from drug_search.bot.keyboards.callbacks import (
    DrugUpdateRequestCallback, AssistantQuestionContinueCallback, BuyDrugRequestCallback
)
from drug_search.bot.keyboards.keyboard_markups import (
    buy_request_keyboard, get_tokens_packages_to_buy_keyboard, get_subscription_packages_keyboard
)
from drug_search.bot.lexicon import MessageTemplates
from drug_search.bot.lexicon.enums import ModeTypes, DrugMenu
from drug_search.bot.lexicon.message_text import MessageText
from drug_search.bot.utils.format_message_text import DrugMessageFormatter
from drug_search.bot.utils.message_actions import open_drug_menu
from drug_search.core.dependencies.bot.cache_service_dep import cache_service
from drug_search.core.lexicon import ARROW_TYPES, JobStatuses, DANGER_CLASSIFICATION
from drug_search.core.schemas import (
    BuyDrugResponse, BuyDrugStatuses, UpdateDrugResponse, UpdateDrugStatuses, UserSchema, DrugExistingResponse,
    DrugSchema
)

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
    await callback_query.answer()

    api_response: UpdateDrugResponse = await api_client.update_drug(
        drug_id=callback_data.drug_id,
        access_token=access_token
    )

    match api_response.status:
        case UpdateDrugStatuses.DRUG_UPDATING:
            await callback_query.message.edit_text(
                text=MessageText.DRUG_UPDATING
            )
        case UpdateDrugStatuses.NOT_ENOUGH_TOKENS:
            keyboard = get_tokens_packages_to_buy_keyboard()
            await callback_query.message.edit_text(
                text=MessageText.NOT_ENOUGH_UPDATE_TOKENS,
                reply_markup=keyboard
            )
        case UpdateDrugStatuses.NEED_PREMIUM:
            await callback_query.message.edit_text(
                text=MessageText.NEED_SUBSCRIPTION_FOR_UPDATE
            )


@router.callback_query(BuyDrugRequestCallback.filter())
async def drug_buy_request(
        callback_query: CallbackQuery,
        state: FSMContext,
        access_token: str,
        api_client: DrugSearchAPIClient
):
    # [ получаем данные из state ]
    await callback_query.answer()

    state_data = await state.get_data()

    drug_name = state_data.get("purchase_drug_name")
    drug_id = state_data.get("purchase_drug_id")
    danger_classification = state_data.get("purchase_danger_classification")

    user = await cache_service.get_user_profile(
        access_token,
        telegram_id=callback_query.from_user.id
    )

    await drug_buy(
        drug_name=drug_name,
        drug_id=drug_id,
        danger_classification=danger_classification,
        message=callback_query.message,
        access_token=access_token,
        api_client=api_client,
        user=user
    )


async def drug_buy(
        message: Message,
        access_token: str,
        api_client: DrugSearchAPIClient,
        drug_name: str,
        user: UserSchema,
        drug_id: uuid.UUID | None,
        danger_classification: DANGER_CLASSIFICATION,
        drug_menu: DrugMenu | None = None,
        is_message_from_user: bool = False,
):
    """Обработка покупки препарата"""
    if not all([drug_name, danger_classification]):
        if not is_message_from_user:
            await message.answer("Данные о препарате устарели")
            return
        else:
            await message.edit_text("Данные о препарате устарели")
            return

    api_response: BuyDrugResponse = await api_client.buy_drug(
        drug_name,
        drug_id,
        danger_classification,
        access_token=access_token,
    )

    if is_message_from_user:
        send_message = message.answer
    else:
        send_message = message.edit_text

    match api_response.status:
        case BuyDrugStatuses.DRUG_CREATED:
            if api_response.job_status == JobStatuses.CREATED:
                logger.info(f"Юзер {message.from_user.id} создал препарат {api_response.drug_name}")
                await send_message(
                    text=MessageText.DRUG_BUY_CREATED
                )
            elif api_response.job_status == JobStatuses.QUEUED:
                await send_message(
                    text=MessageText.DRUG_BUY_QUEUED
                )
        case BuyDrugStatuses.DRUG_ALLOWED:
            await send_message(
                text=MessageText.DRUG_BUY_ALLOWED.format(drug_name=api_response.drug_name)
            )
        case BuyDrugStatuses.NOT_ENOUGH_TOKENS:
            keyboard = get_tokens_packages_to_buy_keyboard()
            await send_message(
                text=MessageText.NOT_ENOUGH_CREATE_TOKENS,
                reply_markup=keyboard
            )
        case BuyDrugStatuses.NEED_PREMIUM:
            keyboard = get_subscription_packages_keyboard(
                subscription_type=user.subscription_type
            )
            await send_message(
                text=MessageText.NEED_SUBSCRIPTION,
                reply_markup=keyboard
            )
        case BuyDrugStatuses.DANGER:
            await send_message(
                text=MessageText.DRUG_IS_BANNED
            )

    # [ если препарат уже был в базе ]
    if drug_id:
        drug: DrugSchema = await api_client.get_drug(
            drug_id=drug_id,
            access_token=access_token
        )

        logger.info(f"Открывается меню препарата {drug.name}: {drug_menu}")
        await open_drug_menu(
            drug=drug,
            drug_menu=drug_menu,
            message=message,
            user=user
        )


@router.callback_query(WrongDrugFoundedCallback.filter())
async def wrong_drug_founded(
        callback_query: CallbackQuery,
        access_token: str,
        state: FSMContext,  # noqa
        callback_data: WrongDrugFoundedCallback,
        api_client: DrugSearchAPIClient
):
    """Клик по 'Найден не тот препарат'"""
    await callback_query.answer()

    user: UserSchema = await cache_service.get_user_profile(access_token, callback_query.from_user.id)
    await callback_query.message.edit_text(MessageText.DRUG_MANUAL_SEARCHING)

    drug_response: DrugExistingResponse = await api_client.search_drug_without_trigrams(
        callback_data.drug_name_query,
        access_token
    )

    logger.info(f"Юзер заново ищет препарат: {callback_data.drug_name_query}")

    if drug_response.is_exist:
        if drug_response.is_allowed:
            message_text: str = DrugMessageFormatter.format_drug_briefly(drug_response.drug)
            await callback_query.message.edit_text(
                message_text,
                reply_markup=drug_keyboard(
                    drug=drug_response.drug,
                    drug_menu=DrugMenu.BRIEFLY,
                    user_subscribe_type=user.subscription_type,
                    mode=ModeTypes.WRONG_DRUG,
                ),
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
        else:
            # [ предложить купить препарат ]
            await state.update_data(
                purchase_drug_name=drug_response.drug_name,
                purchase_drug_id=drug_response.drug.id if drug_response.drug else None,
                purchase_danger_classification=drug_response.danger_classification
            )

            await callback_query.message.edit_text(
                text=MessageTemplates.DRUG_BUY_REQUEST.format(
                    drug_name_ru=drug_response.drug_name_ru
                ),
                reply_markup=buy_request_keyboard(),
            )
    else:
        await callback_query.message.edit_text(MessageText.DRUG_IS_NOT_EXIST)


@router.callback_query(AssistantQuestionContinueCallback.filter())
async def assistant_question_listing(
        callback_query: CallbackQuery,
        callback_data: AssistantQuestionContinueCallback,
        state: FSMContext,  # noqa
        access_token: str,
        api_client: DrugSearchAPIClient
):
    """Продолжить список ответа ассистента"""
    await callback_query.answer()

    arrow: ARROW_TYPES = ARROW_TYPES.FORWARD if callback_data.arrow == ARROW_TYPES.BACK else ARROW_TYPES.BACK
    await api_client.question_drugs_answer(
        access_token=access_token,
        user_telegram_id=str(callback_query.from_user.id),
        question=callback_data.question,
        message_id=str(callback_query.message.message_id),
        arrow=arrow
    )
