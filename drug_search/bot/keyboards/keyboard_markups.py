from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards import DrugListCallback
from lexicon.keyboard_words import ButtonText

# Reply
main_menu_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=ButtonText.PROFILE)],
        [KeyboardButton(text=ButtonText.DRUG_DATABASE)]
    ]
)

# Inline
drug_database_get_full_list = InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=ButtonText.FULL_LIST,
                callback_data=DrugListCallback(page=0).pack()
            )
        ]
    ]
)


def get_drugs_list_keyboard(drugs: list[dict], page: int):
    # Получаем клавиатуру с названиями препов и CallbackData=uuid.UUID

    drug_pages = drugs[::9]  # по 9 препаратов
