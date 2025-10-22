import logging

from aiogram import Router, F
from aiogram.types import Message

from drug_search.bot.lexicon.keyboard_words import ButtonText

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.message(F.text == ButtonText.HELP)
async def get_help(
        message: Message,
):
    ...  # TODO: inline клавиатура с кнопками у сообщения
