import logging

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from drug_search.bot.lexicon.keyboard_words import ButtonText

logger = logging.getLogger(__name__)


def get_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ButtonText.MODES_INFO)],
            [KeyboardButton(text=ButtonText.MODES_INFO_QUIZ)],
            [KeyboardButton(text=ButtonText.PROFILE)],
            [KeyboardButton(text=ButtonText.DRUG_DATABASE)],
            [KeyboardButton(text=ButtonText.HELP)],
        ],
        resize_keyboard=True,
    )
