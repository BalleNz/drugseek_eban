import hashlib
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from drug_search.bot.keyboards.callbacks import ReferralsMenuCallback
from drug_search.bot.keyboards.keyboard_markups import get_free_tokens_menu_keyboard, referrals_menu_keyboard
from drug_search.bot.lexicon.message_text import MessageText
from drug_search.bot.utils.referrals_funcs import get_ref_level
from drug_search.core.lexicon import REFERRALS_REWARDS, BOT_USERNAME
from drug_search.core.schemas import UserSchema
from drug_search.core.services.cache_logic.cache_service import CacheService

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


@router.callback_query(ReferralsMenuCallback.filter())
async def referrals_menu(
        callback_query: CallbackQuery,
        state: FSMContext,  # noqa
        cache_service: CacheService,
        access_token: str
):
    """Меню рефералов"""
    # [ deps ]
    user: UserSchema = await cache_service.get_user_profile(
        access_token,
        str(callback_query.from_user.id)
    )
    user_referrals_count = user.referrals_count

    ref_level = get_ref_level(user_referrals_count)
    ref_tokens_next_level = REFERRALS_REWARDS[ref_level]

    def get_referral_link(user_telegram_id: str, bot_username: str) -> str:
        """Генерация ссылки из ID пользователя"""
        token = hashlib.md5(user_telegram_id.encode()).hexdigest()

        short_token = token[:8]  # "827ccb0e"

        return f"https://t.me/{bot_username}?start=ref_{short_token}"

    text = MessageText.REFERRALS_MENU.format(
        ref_level=ref_level,
        ref_tokens_next_level=ref_tokens_next_level,
        ref_members_count=user_referrals_count,
        url=get_referral_link(user.telegram_id, BOT_USERNAME)
    )

    await callback_query.message.edit_text(
        text=text,
        reply_markup=referrals_menu_keyboard()
    )
