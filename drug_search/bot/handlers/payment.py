import datetime
import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message, PreCheckoutQuery

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.bot.bot_instance import bot
from drug_search.bot.keyboards.callbacks import BuySubscriptionCallback, BuyTokensCallback, \
    BuySubscriptionChosenTypeCallback, BuyDrugPackCallback, BuyDrugPackConfirmationCallback
from drug_search.bot.keyboards.callbacks import BuyTokensConfirmationCallback, BuySubscriptionConfirmationCallback
from drug_search.bot.keyboards.payment_keyboards import get_tokens_packages_to_buy_keyboard, \
    get_subscription_packages_types_keyboard, \
    get_subscription_packages_keyboard, get_drug_packs_keyboard
from drug_search.bot.lexicon.message_text import MessageText
from drug_search.core.lexicon import TokensPackage, SubscriptionPackage, SUBSCRIPTION_TYPES, DrugPackPackage
from drug_search.core.schemas import UserSchema, PaymentRequest
from drug_search.core.services.cache_logic.cache_service import CacheService
from drug_search.core.utils.payment import send_invoice

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


async def buy_tokens(
        query: CallbackQuery | Message,
):
    """Описание пакетов токенов"""
    text = MessageText.TOKENS_BUY
    keyboard = get_tokens_packages_to_buy_keyboard()

    if type(query) is CallbackQuery:
        await query.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    else:
        await query.answer(
            text=text,
            reply_markup=keyboard
        )


@router.callback_query(BuyTokensCallback.filter())
async def buy_tokens_from_callback(
        callback_query: CallbackQuery,
        state: FSMContext,  # noqa
):
    await callback_query.answer()

    await buy_tokens(callback_query)


@router.message(Command("tokens"))
async def buy_tokens_from_command(
        message: Message,
        state: FSMContext,  # noqa
):
    await buy_tokens(message)


@router.callback_query(BuyTokensConfirmationCallback.filter())
async def buy_tokens_conf(
        callback_query: CallbackQuery,
        callback_data: BuyTokensConfirmationCallback,
        state: FSMContext,  # noqa
):
    """Описание пакетов токенов"""
    await callback_query.answer()

    tokens_package = TokensPackage.get_by_key(callback_data.token_package_key)

    text = MessageText.TOKENS_CONFIRMATION.format(
        package_name=tokens_package.name,
        package_price=tokens_package.price,
    )

    await callback_query.message.edit_text(
        text
    )

    await send_invoice(
        callback_query,
        tokens_package.price,
        tokens_package.name,
        tokens_package.key
    )


# [ SUBSCRIPTION PACKAGES ]
async def buy_subscription_choose_type(
        query: CallbackQuery | Message,
        state: FSMContext,  # noqa
        cache_service: CacheService,
        access_token: str
):
    user: UserSchema = await cache_service.get_user_profile(
        access_token,
        str(query.from_user.id)
    )

    text = MessageText.SUBSCRIPTION_BUY_CHOOSE_TYPE

    keyboard: InlineKeyboardMarkup = get_subscription_packages_types_keyboard(user.subscription_type)

    if type(query) is CallbackQuery:
        await query.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    else:
        if user.subscription_type == SUBSCRIPTION_TYPES.PREMIUM:
            await query.answer(
                text="У вас премиум подписка!"
            )
        else:
            await query.answer(
                text=text,
                reply_markup=keyboard
            )


@router.callback_query(BuySubscriptionCallback.filter())
async def buy_subscription_choose_type_from_callback(
        callback_query: CallbackQuery,
        state: FSMContext,  # noqa
        cache_service: CacheService,
        access_token: str
):
    await callback_query.answer()

    await buy_subscription_choose_type(
        callback_query,
        state,
        cache_service,
        access_token
    )


@router.message(Command("subscription"))
async def buy_subscription_choose_type_from_command(
        message: Message,
        state: FSMContext,  # noqa
        cache_service: CacheService,
        access_token: str
):
    await buy_subscription_choose_type(
        message,
        state,
        cache_service,
        access_token
    )


@router.callback_query(BuySubscriptionChosenTypeCallback.filter())
async def buy_subscription_choose_package(
        callback_query: CallbackQuery,
        callback_data: BuySubscriptionChosenTypeCallback,
        access_token: str,
        cache_service: CacheService,
        state: FSMContext,  # noqa
):
    """Выбор пакета подписки"""
    await callback_query.answer()

    user: UserSchema = await cache_service.get_user_profile(
        access_token,
        str(callback_query.from_user.id)
    )

    chosen_subscription_text: str = ""
    match callback_data.subscription_type:
        case SUBSCRIPTION_TYPES.LITE:
            chosen_subscription_text = "(Лайт)"
        case SUBSCRIPTION_TYPES.PREMIUM:
            chosen_subscription_text = "(Премиум)"

    text = MessageText.SUBSCRIPTION_BUY_CHOOSE_DURATION.format(
        subscription_type=chosen_subscription_text
    )

    keyboard = get_subscription_packages_keyboard(
        chosen_subscription_type=callback_data.subscription_type,
        subscription_days=user.subscription_days_remaining
    )

    await callback_query.message.edit_text(
        text=text,
        reply_markup=keyboard
    )


@router.callback_query(BuySubscriptionConfirmationCallback.filter())
async def buy_subscription_confirmation(
        callback_query: CallbackQuery,
        callback_data: BuySubscriptionConfirmationCallback,
        cache_service: CacheService,
        access_token: str,
        state: FSMContext,  # noqa
):
    """Переход по ссылке для покупки"""
    await callback_query.answer()

    user: UserSchema = await cache_service.get_user_profile(
        access_token,
        str(callback_query.from_user.id)
    )

    subscription_key = callback_data.subscription_package_key
    subscription_package: SubscriptionPackage = SubscriptionPackage.get_by_key(subscription_key)
    price: int = subscription_package.price(user.subscription_days_remaining)

    subscription_end = (datetime.datetime.now() + datetime.timedelta(days=subscription_package.duration)).strftime(
        "%d.%m.%Y")

    text = MessageText.SUBSCRIPTION_BUY_CONFIRMATION.format(
        subscription_name=subscription_package.subscription_type_text,
        subscription_period=subscription_package.duration,
        subscription_price=price,
        subscription_end=subscription_end,
    )

    await callback_query.message.edit_text(
        text
    )

    await send_invoice(
        callback_query,
        price,
        subscription_package.name,
        subscription_key
    )


# [ DRUG PACKS ]
async def buy_drug_packs(query: CallbackQuery | Message):
    text = MessageText.DRUG_PACKS_BUY
    keyboard = get_drug_packs_keyboard()

    if type(query) is CallbackQuery:
        await query.message.edit_text(text=text, reply_markup=keyboard)
    else:
        await query.answer(text=text, reply_markup=keyboard)


@router.callback_query(BuyDrugPackCallback.filter())
async def buy_drug_packs_from_callback(callback_query: CallbackQuery, state: FSMContext):  # noqa
    await callback_query.answer()
    await buy_drug_packs(callback_query)


@router.message(Command("packs"))
async def buy_drug_packs_from_command(message: Message, state: FSMContext):  # noqa
    await buy_drug_packs(message)


@router.callback_query(BuyDrugPackConfirmationCallback.filter())
async def buy_drug_pack_confirmation(
        callback_query: CallbackQuery,
        callback_data: BuyDrugPackConfirmationCallback,
        state: FSMContext,  # noqa
):
    await callback_query.answer()

    pack = DrugPackPackage.get_by_key(callback_data.pack_key)
    text = MessageText.DRUG_PACK_CONFIRMATION.format(
        pack_name=pack.name,
        pack_description=pack.description,
        pack_price=pack.price,
    )

    await callback_query.message.edit_text(text)
    await send_invoice(
        callback_query,
        pack.price,
        pack.name,
        pack.key,
    )


# [ Обработка оплаты ]
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    """Ожидание оплаты"""
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(
        message: Message,
        access_token: str,
        api_client: DrugSearchAPIClient,
        cache_service: CacheService
):
    payment_info = message.successful_payment
    payload = payment_info.invoice_payload

    logger.info(f"New invoice payload: {payload}")

    product_key, user_id_from_payload = payload.split('-')

    user: UserSchema = await cache_service.get_user_profile(
        access_token,
        str(message.from_user.id)
    )

    request = PaymentRequest(
        product_key=product_key,
        user_telegram_id=user_id_from_payload,
        sub_days=user.subscription_days_remaining
    )

    await api_client.payment_process(
        access_token,
        request
    )
