from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from lexicon.keyboard_words import ButtonText

main_menu_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=ButtonText.PROFILE)],
        [KeyboardButton(text=ButtonText.DRUG_DATABASE)]
    ]
)
