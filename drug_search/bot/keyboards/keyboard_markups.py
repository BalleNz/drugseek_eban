import uuid
from datetime import datetime

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from drug_search.bot.keyboards import (DrugDescribeCallback, DrugListCallback, DescribeTypes,
                                       WrongDrugFoundedCallback)
from drug_search.bot.keyboards.callbacks import BuyDrugRequestCallback, AssistantQuestionContinue, \
    DrugUpdateRequestCallback
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.core.lexicon import SUBSCRIBE_TYPES, DANGER_CLASSIFICATION, ARROW_TYPES
from drug_search.core.schemas import DrugBrieflySchema
from drug_search.core.utils.funcs import may_update_drug

# [Reply]
menu_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=ButtonText.PROFILE)],
        [KeyboardButton(text=ButtonText.DRUG_DATABASE)]
    ],
    resize_keyboard=True,
)

# [Inline]
drug_database_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
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


def drug_list_keyboard(drugs: list[DrugBrieflySchema], page: int) -> InlineKeyboardMarkup:
    """
    Клавиатура с названиями препов и CallbackData
    """

    if drugs is None:
        return InlineKeyboardMarkup(inline_keyboard=[])

    drugs_count_on_one_page = 6
    drug_pages = [drugs[i:i + drugs_count_on_one_page] for i in range(0, len(drugs), drugs_count_on_one_page)]
    buttons = []

    for drug in drug_pages[page]:
        # проходит по массиву в текущей странице page
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

    # [ arrows logic ]
    if page > 0:
        buttons[-1].append(
            InlineKeyboardButton(
                text=ButtonText.LEFT_ARROW,
                callback_data=DrugListCallback(
                    arrow=ARROW_TYPES.BACK,
                    page=page - 1
                ).pack()
            )
        )
    if len(drug_pages) - 1 - page:
        buttons[-1].append(
            InlineKeyboardButton(
                text=ButtonText.RIGHT_ARROW,
                callback_data=DrugListCallback(
                    arrow=ARROW_TYPES.FORWARD,
                    page=page + 1
                ).pack()
            )
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def drug_keyboard(
        drug_id: uuid.UUID,
        describe_type: DescribeTypes,
        user_subscribe_type: SUBSCRIBE_TYPES,
        drug_last_update: datetime | None,  # для кнопки "обновить", только в главном меню
        page: int | None = None,  # страница с прошлого меню
        drug_name: str | None = None  # если найден неверный препарат
) -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру по describe_type:
    а) с выбором разделов препарата,
    б) со стрелкой возвращения в меню листинг
    """
    if describe_type != DescribeTypes.BRIEFLY:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=ButtonText.LEFT_ARROW,
                        callback_data=DrugDescribeCallback(
                            describe_type=DescribeTypes.BRIEFLY,
                            drug_id=drug_id,
                            page=page
                        ).pack()
                    )
                ]
            ]
        )
        if describe_type == DescribeTypes.UPDATE_INFO:
            keyboard.inline_keyboard.insert(
                0,
                [
                    InlineKeyboardButton(
                        text=ButtonText.UPDATE_DRUG if user_subscribe_type != SUBSCRIBE_TYPES.PREMIUM else ButtonText.UPDATE_DRUG_FOR_PREMIUM,
                        callback_data=DrugUpdateRequestCallback(
                            drug_id=drug_id
                        ).pack()
                    )
                ]
            )
        elif describe_type == DescribeTypes.RESEARCHES:
            keyboard.inline_keyboard.insert(
                0,
                [
                    InlineKeyboardButton(
                        text=ButtonText.UPDATE_RESEARCHES,
                        callback_data=...
                    )
                ]
            )

        return keyboard

    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ButtonText.DOSAGES,
                    callback_data=DrugDescribeCallback(
                        describe_type=DescribeTypes.DOSAGES,
                        drug_id=drug_id,
                        page=page
                    ).pack()
                ),
                InlineKeyboardButton(
                    text=ButtonText.METABOLISM,
                    callback_data=DrugDescribeCallback(
                        describe_type=DescribeTypes.METABOLISM,
                        drug_id=drug_id,
                        page=page
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=ButtonText.COMBINATIONS,
                    callback_data=DrugDescribeCallback(
                        describe_type=DescribeTypes.COMBINATIONS,
                        drug_id=drug_id,
                        page=page
                    ).pack()
                ),
                InlineKeyboardButton(
                    text=ButtonText.ANALOGS,
                    callback_data=DrugDescribeCallback(
                        describe_type=DescribeTypes.ANALOGS,
                        drug_id=drug_id,
                        page=page
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=ButtonText.MECHANISM,
                    callback_data=DrugDescribeCallback(
                        describe_type=DescribeTypes.MECHANISM,
                        drug_id=drug_id,
                        page=page
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=ButtonText.RESEARCHES,
                    callback_data=DrugDescribeCallback(
                        describe_type=DescribeTypes.RESEARCHES,
                        drug_id=drug_id,
                        page=page,
                    ).pack()
                )
            ],
        ]
    )

    if drug_last_update and may_update_drug(drug_last_update) and describe_type == DescribeTypes.BRIEFLY:
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=ButtonText.UPDATE_DRUG,
                    callback_data=DrugDescribeCallback(
                        describe_type=describe_type.UPDATE_INFO,
                        drug_id=drug_id,
                        page=page
                    ).pack()
                )
            ]
        )

    if page is not None:
        # если просмотр с кнопки "база данных"
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=ButtonText.RIGHT_ARROW,
                    callback_data=DrugListCallback(
                        page=page
                    ).pack()
                )
            ]
        )
    elif drug_name:
        # если просмотр с поиска
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=ButtonText.WRONG_DRUG_FOUNDED,
                    callback_data=WrongDrugFoundedCallback(
                        drug_name_query=drug_name
                    ).pack()
                )
            ]
        )
    return keyboard


def buy_request_keyboard(
        drug_name: str,
        drug_id: uuid.UUID | None,  # Может не быть —> создается новый препарат.
        danger_classification: DANGER_CLASSIFICATION
) -> InlineKeyboardMarkup:
    """
    Клавиатура с покупкой препарата.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ButtonText.BUY_DRUG,
                    callback_data=BuyDrugRequestCallback(
                        drug_id=drug_id if drug_id else None,
                        drug_name=drug_name,
                        danger_classification=danger_classification
                    ).pack()
                )
            ]
        ]
    )


def question_continue_keyboard(
        question: str,
        arrow: ARROW_TYPES
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ButtonText.RIGHT_ARROW if arrow == arrow.FORWARD else ButtonText.LEFT_ARROW,
                    callback_data=AssistantQuestionContinue(
                        question=question,
                        arrow=arrow
                    ).pack()
                )
            ]
        ]
    )
