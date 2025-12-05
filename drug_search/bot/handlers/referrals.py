import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.bot.bot_instance import bot
from drug_search.bot.keyboards.callbacks import ReferralsMenuCallback, GetTokensForSubscriptionCallback
from drug_search.bot.keyboards.keyboard_markups import get_free_tokens_menu_keyboard, referrals_menu_keyboard, \
    get_tokens_for_subscription_channel_list
from drug_search.bot.lexicon.message_text import MessageText
from drug_search.core.lexicon import REFERRALS_REWARDS, BOT_USERNAME, REFERRALS_LEVELS, CHANNELS_USERNAME_FREE_TOKENS
from drug_search.core.schemas import UserSchema
from drug_search.core.services.cache_logic.cache_service import CacheService
from drug_search.core.utils.referrals_funcs import get_ref_level, generate_referral_url, is_user_subscribed

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.message(Command("free_tokens"))
async def free_tokens(
        message: Message,
        state: FSMContext,  # noqa
        cache_service: CacheService,
        access_token: str
):
    """Меню с токенами за подписку"""
    # [ deps ]
    user: UserSchema = await cache_service.get_user_profile(access_token, str(message.from_user.id))

    keyboard = get_free_tokens_menu_keyboard(user.got_free_tokens)

    await message.answer(
        text=MessageText.GET_FREE_TOKENS_MENU,
        reply_markup=keyboard
    )


@router.callback_query(GetTokensForSubscriptionCallback.filter())
async def tokens_for_subscription(
        callback_query: CallbackQuery,
        state: FSMContext,  # noqa
        api_client: DrugSearchAPIClient,
        access_token: str
):
    """токены за подписку"""
    all_subscribed = True
    channels_username_check = list(tuple())
    for channel_username in CHANNELS_USERNAME_FREE_TOKENS:
        is_subscribed: bool = await is_user_subscribed(
            callback_query.from_user.id,
            channel_username,
            bot=bot
        )

        if not is_subscribed:
            all_subscribed = False

        channels_username_check.append((channel_username, is_subscribed))

    if all_subscribed:  # если подписки есть
        await api_client.get_free_tokens(access_token)
        await callback_query.message.edit_text(
            text="<b>Вам начислены бонусные токены!</b>"
        )

    else:
        await callback_query.message.edit_text(
            text="🧚‍♀️ Подпишись на эти каналы, чтобы получить бонус",
            reply_markup=get_tokens_for_subscription_channel_list(channels_username_check)
        )


async def referrals_menu(
        query: CallbackQuery | Message,
        cache_service: CacheService,
        access_token: str
):
    """Меню рефералов"""
    # [ deps ]
    user: UserSchema = await cache_service.get_user_profile(
        access_token,
        str(query.from_user.id)
    )
    user_referrals_count = user.referrals_count

    ref_level = get_ref_level(user_referrals_count)
    ref_tokens_next_level = REFERRALS_REWARDS[ref_level + 1]

    def tokens_text(tokens: int) -> str:
        """
        Возвращает строку с правильным склонением слова 'токен'
        в зависимости от переданного числа.
        """
        if 11 <= tokens % 100 <= 14:
            return f"{tokens} токенов"

        last_digit = tokens % 10

        if last_digit == 1:
            return f"{tokens} токен"
        elif 2 <= last_digit <= 4:
            return f"{tokens} токена"
        else:
            return f"{tokens} токенов"

    referrals_count_next = REFERRALS_LEVELS[ref_level + 1] - user_referrals_count
    referrals_count_next_text = str(referrals_count_next) + " человек" if referrals_count_next != 1 else "1 человека"

    url=generate_referral_url(user.telegram_id, BOT_USERNAME)

    text = MessageText.REFERRALS_MENU.format(
        ref_tokens_next_level_text=tokens_text(ref_tokens_next_level),
        referrals_count_next_text=referrals_count_next_text,
        url=url
    )

    keyboard = referrals_menu_keyboard(url)
    if type(query) is CallbackQuery:
        await query.message.edit_text(
            text=text,
            reply_markup=keyboard,
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
    else:
        await query.answer(
            text=text,
            reply_markup=keyboard,
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )


@router.callback_query(ReferralsMenuCallback.filter())
async def referrals_menu_from_callback(
        callback_query: CallbackQuery,
        state: FSMContext,  # noqa
        cache_service: CacheService,
        access_token: str
):
    await referrals_menu(
        callback_query,
        cache_service,
        access_token
    )


@router.message(Command("referrals"))
async def referrals_menu_from_command(
        message: Message,
        state: FSMContext,  # noqa
        cache_service: CacheService,
        access_token: str
):
    await referrals_menu(
        message,
        cache_service,
        access_token
    )
