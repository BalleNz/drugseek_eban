import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from lexicon import MessageText
from lexicon.keyboard_words import ButtonText
from services.cache_service import CacheService
from states.states import States

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.message(F.text == ButtonText.PROFILE)
async def get_profife_info(
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


"""@router.callback_query(CallbackData())
async def _hui():
    pass"""
