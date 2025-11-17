import logging
from typing import Union

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup

from drug_search.bot.keyboards.callbacks import UserDescriptionCallback, BackToUserProfileCallback
from drug_search.bot.keyboards.keyboard_markups import back_to_user_profile, user_profile_keyboard
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.bot.lexicon.message_text import MessageText
from drug_search.core.schemas import UserSchema
from drug_search.core.services.cache_logic.cache_service import CacheService

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(UserDescriptionCallback.filter())
async def show_description(
        callback_query: CallbackQuery,
        cache_service: CacheService,
        access_token: str,
        state: FSMContext,  # noqa
):
    """Описание юзера"""
    await callback_query.answer()

    telegram_id: str = str(callback_query.from_user.id)

    profile_info: UserSchema = await cache_service.get_user_profile(
        access_token=access_token,
        telegram_id=telegram_id,
    )
    await callback_query.message.edit_text(
        text=MessageText.formatters.USER_PROFILE_DESCRIPTION(user=profile_info),
        reply_markup=back_to_user_profile()
    )


async def _show_user_profile(
        obj: Union[Message, CallbackQuery],
        cache_service: CacheService,
        access_token: str,
        state: FSMContext,  # noqa
):
    """Общая логика отображения профиля"""
    telegram_id = str(obj.from_user.id)

    profile_info: UserSchema = await cache_service.get_user_profile(
        access_token=access_token,
        telegram_id=telegram_id,
    )

    text = MessageText.formatters.USER_PROFILE(user=profile_info)

    keyboard: InlineKeyboardMarkup = user_profile_keyboard(profile_info)

    if isinstance(obj, Message):
        await obj.answer(text=text, reply_markup=keyboard)
    else:
        await obj.message.edit_text(text=text, reply_markup=keyboard)


@router.callback_query(BackToUserProfileCallback.filter())
async def get_profile_from_callback(
        callback: CallbackQuery,
        cache_service: CacheService,
        access_token: str,
        state: FSMContext,
):
    await callback.answer()

    await _show_user_profile(callback, cache_service, access_token, state)


@router.message(F.text == ButtonText.PROFILE)
async def get_profile_from_message(
        message: Message,
        cache_service: CacheService,
        access_token: str,
        state: FSMContext,
):
    await _show_user_profile(message, cache_service, access_token, state)
