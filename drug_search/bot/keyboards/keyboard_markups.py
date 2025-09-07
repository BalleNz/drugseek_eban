from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from drug_search.bot.keyboards import DrugDescribeCallback, DrugListCallback
from drug_search.bot.keyboards.callbacks import DescribeTypes
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.core.schemas.telegram_schemas import DrugBriefly

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


def get_drugs_list_keyboard(drugs: list[DrugBriefly], page: int):
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

    # сделать логику стрелочек:
    # 1. вперед, если есть хотя бы один преп в drug_pages[page+1]
    # 2. назад, если page > 1
    # 3. хуй?
