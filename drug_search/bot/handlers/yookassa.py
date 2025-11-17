import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from drug_search.bot.keyboards.callbacks import BuySubscriptionCallback, BuyTokensCallback
from drug_search.bot.keyboards.callbacks import BuyTokensConfirmationCallback, BuySubscriptionConfirmationCallback
from drug_search.bot.keyboards.keyboard_markups import get_tokens_packages_to_buy_keyboard, get_url_to_buy_keyboard, \
    get_subscription_packages_types_keyboard, get_subscription_packages_keyboard
from drug_search.bot.lexicon.message_text import MessageText
from drug_search.core.lexicon import TokenPackage, SubscriptionPackage, SUBSCRIPTION_TYPES
from drug_search.core.schemas import UserSchema
from drug_search.core.services.cache_logic.cache_service import CacheService
from keyboards.callbacks import BuySubscriptionChosenTypeCallback, FinishPaymentCallback

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.callback_query(BuyTokensCallback.filter())
async def buy_tokens(
        callback_query: CallbackQuery,
        state: FSMContext,  # noqa
):
    """Описание пакетов токенов"""
    await callback_query.answer()

    text = MessageText.TOKENS_BUY
    keyboard = get_tokens_packages_to_buy_keyboard()

    await callback_query.message.edit_text(
        text=text,
        reply_markup=keyboard
    )


@router.callback_query(BuyTokensConfirmationCallback.filter())
async def buy_tokens_conf(
        callback_query: CallbackQuery,
        callback_data: BuyTokensConfirmationCallback,
        state: FSMContext,
):
    """Описание пакетов токенов"""
    await callback_query.answer()

    tokens_package = TokenPackage.get_by_key(callback_data.token_package_key)

    text = MessageText.TOKENS_CONFIRMATION.format(
        package_name=tokens_package.name,
        package_tokens=tokens_package.amount,
    )

    url = ...

    keyboard = get_url_to_buy_keyboard(
        url="vk.com"
    )

    await callback_query.message.edit_text(
        text=text,
        reply_markup=keyboard
    )


# [ SUBSCRIPTION PACKAGES ]

@router.callback_query(BuySubscriptionCallback.filter())
async def buy_subscription_choose_type(
        callback_query: CallbackQuery,
        state: FSMContext,  # noqa
        cache_service: CacheService,
        access_token: str
):
    await callback_query.answer()

    user: UserSchema = await cache_service.get_user_profile(
        access_token,
        str(callback_query.from_user.id)
    )

    text = MessageText.SUBSCRIPTION_BUY_CHOOSE_TYPE

    keyboard: InlineKeyboardMarkup | None = None
    if user.subscription_type == SUBSCRIPTION_TYPES.DEFAULT:
        keyboard = get_subscription_packages_types_keyboard()

    await callback_query.message.edit_text(
        text=text,
        reply_markup=keyboard
    )


@router.callback_query(BuySubscriptionChosenTypeCallback.filter())
async def buy_subscription_choose_package(
        callback_query: CallbackQuery,
        callback_data: BuySubscriptionChosenTypeCallback,
        state: FSMContext,  # noqa
):
    """Выбор пакета подписки"""
    await callback_query.answer()

    text = MessageText.SUBSCRIPTION_BUY_CHOOSE_DURATION

    keyboard = get_subscription_packages_keyboard(callback_data.subscription_type)

    await callback_query.message.edit_text(
        text=text,
        reply_markup=keyboard
    )


@router.callback_query(BuySubscriptionConfirmationCallback.filter())
async def buy_subscription_confirmation(
        callback_query: CallbackQuery,
        callback_data: BuySubscriptionConfirmationCallback,
        state: FSMContext,  # noqa
):
    """Переход по ссылке для покупки"""
    await callback_query.answer()

    subscription_key = callback_data.subscription_package_key
    subscription_package: SubscriptionPackage = SubscriptionPackage.get_by_key(subscription_key)

    text = MessageText.SUBSCRIPTION_BUY_CONFIRMATION.format(
        subscription_name=subscription_package.name,
        subscription_period=subscription_package.duration,
        subscription_price=subscription_package.price,
    )

    url = ...

    keyboard = get_url_to_buy_keyboard(
        url="vk.com"
    )

    await callback_query.message.edit_text(
        text=text,
        reply_markup=keyboard
    )


@router.callback_query(FinishPaymentCallback.filter())
async def finish_payment(
        callback_query: CallbackQuery,
        state: FSMContext,  # noqa
):
    """После перехода к оплате"""
    await callback_query.answer()

    text = MessageText.FINISH_PAYMENT

    await callback_query.message.edit_text(
        text=text
    )
