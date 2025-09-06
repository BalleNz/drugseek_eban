from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from lexicon.keyboard_words import ButtonText

# Reply
main_menu_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=ButtonText.PROFILE)],
        [KeyboardButton(text=ButtonText.DRUG_DATABASE)]
    ]
)

# Inline
def get_drugs_menu_inline(drugs: list[dict], page: int):
    # Получаем клавиатуру с названиями препов и CallbackData=uuid.UUID

    drug_pages = drugs[::9]  # по 9 препаратов