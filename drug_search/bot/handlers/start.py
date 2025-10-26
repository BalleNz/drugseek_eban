import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from drug_search.bot.keyboards.keyboard_markups import menu_keyboard
from lexicon.message_text import MessageText

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.message(CommandStart())
async def start_dialog(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=MessageText.HELLO, reply_markup=menu_keyboard)
    logger.info(f"User {message.from_user.id} has started dialog.")
