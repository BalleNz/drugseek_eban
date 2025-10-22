import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from drug_search.bot.lexicon import MessageText
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.bot.states.states import States
from services.cache_logic.cache_service import CacheService

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.message(F.text == ButtonText.PROFILE)
async def get_profile_info(
        message: Message,
        cache_service: CacheService,
        access_token: str,
        state: FSMContext,
):
    """Показывает профиль юзера с информацией"""
    await state.set_state(States.PROFILE)

    telegram_id: str = str(message.from_user.id)

    profile_info = await cache_service.get_user_profile(
        access_token=access_token,
        telegram_id=telegram_id,
    )
    await message.answer(
        text=MessageText.format_user_profile(profile_info)
    )
