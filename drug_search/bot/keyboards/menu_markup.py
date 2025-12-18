import logging

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from drug_search.bot.lexicon.keyboard_words import ButtonText

logger = logging.getLogger(__name__)

# [Reply]
menu_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=ButtonText.PROFILE)],
        [KeyboardButton(text=ButtonText.DRUG_DATABASE)],
        [KeyboardButton(text=ButtonText.HELP)],
        #
    ],
    resize_keyboard=True,
)
