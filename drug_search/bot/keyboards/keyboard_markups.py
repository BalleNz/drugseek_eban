from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from drug_search.bot.keyboards import DrugDescribeCallback, DrugListCallback
from drug_search.bot.keyboards.callbacks import DescribeTypes
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.core.schemas.telegram_schemas import DrugBriefly
from keyboards.callbacks import ArrowTypes

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


def get_drugs_list_keyboard(drugs: list[DrugBriefly], page: int) -> InlineKeyboardMarkup:
    # Получаем клавиатуру с названиями препов и CallbackData=uuid.UUID

    drugs_count_on_one_page = 6
    drug_pages = [drugs[i:i + drugs_count_on_one_page] for i in range(0, len(drugs), drugs_count_on_one_page)]
    buttons = []

    for drug in drug_pages[page]:
        # проходит по массиву из страниц препаратов в текущей странице page
        buttons.append(
            InlineKeyboardButton(
                text=drug.drug_name_ru,
                callback_data=DrugDescribeCallback(
                    drug_id=drug.id,
                    describe_type=DescribeTypes.BRIEFLY
                ).pack()
            )
        )

    # arrows logic
    if page > 1:
        buttons.append(
            InlineKeyboardButton(
                text="<——",
                callback_data=DrugListCallback(
                    arrow=ArrowTypes.BACK,
                    page=page-1
                ).pack()
            )
        )
    if len(drug_pages) - page:
        buttons.append(
            InlineKeyboardButton(
                text="——>",
                callback_data=DrugListCallback(
                    arrow=ArrowTypes.FORWARD,
                    page=page + 1
                ).pack()
            )
        )
    return InlineKeyboardMarkup(*buttons)
