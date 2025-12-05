import datetime
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from drug_search.bot.keyboards.callbacks import BuySubscriptionCallback, BuyTokensCallback, \
    BuySubscriptionChosenTypeCallback
from drug_search.bot.keyboards.callbacks import BuyTokensConfirmationCallback, BuySubscriptionConfirmationCallback
from drug_search.bot.keyboards.keyboard_markups import get_tokens_packages_to_buy_keyboard, get_url_to_buy_keyboard, \
    get_subscription_packages_types_keyboard, get_subscription_packages_keyboard
from drug_search.bot.lexicon.message_text import MessageText
from drug_search.core.lexicon import TokenPackage, SubscriptionPackage, SUBSCRIPTION_TYPES
from drug_search.core.schemas import UserSchema
from drug_search.core.services.cache_logic.cache_service import CacheService

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
        user_subscription_type=user.subscription_type,
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
    subscription_price: float = subscription_package.price(user.subscription_days_remaining)

    subscription_end = (datetime.datetime.now() + datetime.timedelta(days=subscription_package.duration)).strftime(
        "%d.%m.%Y")

    text = MessageText.SUBSCRIPTION_BUY_CONFIRMATION.format(
        subscription_name=subscription_package.subscription_type,
        subscription_period=subscription_package.duration,
        subscription_price=subscription_price,
        subscription_end=subscription_end,
    )

    url = ...  # TODO

    keyboard = get_url_to_buy_keyboard(
        url="vk.com"
    )

    await callback_query.message.edit_text(
        text=text,
        reply_markup=keyboard
    )
