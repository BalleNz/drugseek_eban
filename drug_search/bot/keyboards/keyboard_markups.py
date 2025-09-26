import uuid

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from drug_search.bot.keyboards import DrugDescribeCallback, DrugListCallback, DescribeTypes, ArrowTypes
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.core.schemas.telegram_schemas import DrugBriefly

# Reply
main_menu_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=ButtonText.PROFILE)],
        [KeyboardButton(text=ButtonText.DRUG_DATABASE)]
    ],
    resize_keyboard=True,
)

# Inline
drug_database_list_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=ButtonText.FULL_LIST,
                callback_data=DrugListCallback(page=0).pack()
            )
        ]
    ],
    resize_keyboard=True,
)


def get_drug_list_keyboard(drugs: list[DrugBriefly], page: int) -> InlineKeyboardMarkup:
    """Клавиатура с названиями препов и CallbackData"""

    if drugs is None:
        return InlineKeyboardMarkup(inline_keyboard=[])

    drugs_count_on_one_page = 6
    drug_pages = [drugs[i:i + drugs_count_on_one_page] for i in range(0, len(drugs), drugs_count_on_one_page)]
    buttons = []

    for drug in drug_pages[page]:
        # проходит по массиву из страниц препаратов в текущей странице page
        buttons.append(
            [
                InlineKeyboardButton(
                    text=drug.drug_name_ru,
                    callback_data=DrugDescribeCallback(
                        drug_id=drug.drug_id,
                        describe_type=DescribeTypes.BRIEFLY,
                        page=page
                    ).pack()
                )
            ]
        )

    buttons.append([])

    # arrows logic
    if page > 0:
        buttons[-1].append(
            InlineKeyboardButton(
                text="<——",
                callback_data=DrugListCallback(
                    arrow=ArrowTypes.BACK,
                    page=page - 1
                ).pack()
            )
        )
    if len(drug_pages) - 1 - page:
        buttons[-1].append(
            InlineKeyboardButton(
                text="——>",
                callback_data=DrugListCallback(
                    arrow=ArrowTypes.FORWARD,
                    page=page + 1
                ).pack()
            )
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def drug_describe_types_keyboard(
        drug_id: uuid.UUID,
        page: int,  # страница с прошлого меню
        describe_type: DescribeTypes
) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с выбором разделов препарата,
    или со стрелкой возвращения в меню листинга (в зависимости от describe_type)
    """
    if describe_type != DescribeTypes.BRIEFLY:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="<——",
                        callback_data=DrugDescribeCallback(
                            describe_type=DescribeTypes.BRIEFLY,
                            drug_id=drug_id,
                            page=page
                        ).pack()
                    )
                ]
            ]
        )

    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Дозировки",
                    callback_data=DrugDescribeCallback(
                        describe_type=DescribeTypes.DOSAGES,
                        drug_id=drug_id,
                        page=page
                    ).pack()
                ),
                InlineKeyboardButton(
                    text="Метаболизм",
                    callback_data=DrugDescribeCallback(
                        describe_type=DescribeTypes.METABOLISM,
                        drug_id=drug_id,
                        page=page
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="Комбинации",
                    callback_data=DrugDescribeCallback(
                        describe_type=DescribeTypes.COMBINATIONS,
                        drug_id=drug_id,
                        page=page
                    ).pack()
                ),
                InlineKeyboardButton(
                    text="Аналоги",
                    callback_data=DrugDescribeCallback(
                        describe_type=DescribeTypes.ANALOGS,
                        drug_id=drug_id,
                        page=page
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="Механизм действия | Пути активации",
                    callback_data=DrugDescribeCallback(
                        describe_type=DescribeTypes.PATHWAYS,
                        drug_id=drug_id,
                        page=page
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="Научные исследования",
                    callback_data=DrugDescribeCallback(
                        describe_type=DescribeTypes.RESEARCHES,
                        drug_id=drug_id,
                        page=page
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="<——",
                    callback_data=DrugListCallback(
                        page=page
                    ).pack()
                )
            ]
        ]
    )
    return keyboard


def drug_describe_menu_keyboard(
        drug_id: uuid.UUID,
        page: int
):
    """Клавиатура во время просмотра одного из разделов препарата.
    Имеет только стрелку возвращения в листинг.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="<——",
                    callback_data=DrugDescribeCallback(
                        drug_id=drug_id,
                        describe_type=DescribeTypes.BRIEFLY,
                        page=page
                    ).pack()
                )
            ]
        ]
    )
