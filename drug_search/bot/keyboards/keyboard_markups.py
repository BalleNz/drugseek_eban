from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from drug_search.bot.keyboards import (DrugDescribeCallback, DrugListCallback, DescribeTypes,
                                       WrongDrugFoundedCallback)
from drug_search.bot.keyboards.callbacks import BuyDrugRequestCallback, AssistantQuestionContinue, \
    DrugUpdateRequestCallback, UserDescriptionCallback, HelpSectionCallback
from drug_search.bot.lexicon.enums import ModeTypes, UserDescriptionMode, HelpSectionMode
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.core.lexicon import SUBSCRIBE_TYPES, ARROW_TYPES
from drug_search.core.schemas import DrugBrieflySchema, DrugSchema
from drug_search.core.utils.funcs import may_update_drug

# [Reply]
menu_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=ButtonText.PROFILE)],
        [KeyboardButton(text=ButtonText.HELP)],
        [KeyboardButton(text=ButtonText.DRUG_DATABASE)],
    ],
    resize_keyboard=True,
)


# [Inline]
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
        drug: DrugSchema,
        describe_type: DescribeTypes,
        user_subscribe_type: SUBSCRIBE_TYPES,
        mode: ModeTypes,
        page: int | None = None,  # страница с прошлого меню
        user_query: str | None = None
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
                            drug_id=drug.id,
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
                            drug_id=drug.id
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
                        callback_data=...  # TODO
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
                        drug_id=drug.id,
                        page=page
                    ).pack()
                ),
                InlineKeyboardButton(
                    text=ButtonText.METABOLISM,
                    callback_data=DrugDescribeCallback(
                        describe_type=DescribeTypes.METABOLISM,
                        drug_id=drug.id,
                        page=page
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=ButtonText.COMBINATIONS,
                    callback_data=DrugDescribeCallback(
                        describe_type=DescribeTypes.COMBINATIONS,
                        drug_id=drug.id,
                        page=page
                    ).pack()
                ),
                InlineKeyboardButton(
                    text=ButtonText.ANALOGS,
                    callback_data=DrugDescribeCallback(
                        describe_type=DescribeTypes.ANALOGS,
                        drug_id=drug.id,
                        page=page
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=ButtonText.MECHANISM,
                    callback_data=DrugDescribeCallback(
                        describe_type=DescribeTypes.MECHANISM,
                        drug_id=drug.id,
                        page=page
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=ButtonText.RESEARCHES,
                    callback_data=DrugDescribeCallback(
                        describe_type=DescribeTypes.RESEARCHES,
                        drug_id=drug.id,
                        page=page,
                    ).pack()
                )
            ],
        ]
    )

    if mode == ModeTypes.DATABASE and may_update_drug(drug.updated_at) and describe_type == DescribeTypes.BRIEFLY:
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=ButtonText.UPDATE_DRUG,
                    callback_data=DrugDescribeCallback(
                        describe_type=describe_type.UPDATE_INFO,
                        drug_id=drug.id,
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
                    text=ButtonText.LEFT_ARROW,
                    callback_data=DrugListCallback(
                        page=page
                    ).pack()
                )
            ]
        )
    elif mode == ModeTypes.SEARCH:
        # если просмотр с поиска
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=ButtonText.WRONG_DRUG_FOUNDED,
                    callback_data=WrongDrugFoundedCallback(
                        drug_name_query=user_query if user_query.__len__() < 25 else user_query[:25]
                    ).pack()
                )
            ]
        )
    return keyboard


def buy_request_keyboard(
        maybe_wrong_drug: bool = False,
        user_query: str = None
) -> InlineKeyboardMarkup:
    """
    Клавиатура с покупкой препарата.
    """
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ButtonText.BUY_DRUG,
                    callback_data=BuyDrugRequestCallback().pack()
                )
            ]
        ]
    )

    if maybe_wrong_drug:
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=ButtonText.WRONG_DRUG_FOUNDED,
                    callback_data=WrongDrugFoundedCallback(
                        drug_name_query=user_query
                    ).pack()
                )
            ]
        )
    return keyboard


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


# [ USER PROFILE ]
def user_description_keyboard(
        mode: UserDescriptionMode
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ButtonText.LEFT_ARROW if mode == UserDescriptionMode.BACK_TO_PROFILE else ButtonText.SHOW_DESCRIPTION,
                    callback_data=UserDescriptionCallback(
                        mode=mode
                    ).pack()
                )
            ]
        ]
    )


def get_help_keyboard(
        help_mode: HelpSectionMode
):
    keyboard: InlineKeyboardMarkup

    menu_buttons = {
        HelpSectionMode.MAIN: [
            (ButtonText.HELP_QUERIES, HelpSectionMode.QUERIES),
            (ButtonText.HELP_TOKENS, HelpSectionMode.TOKENS),
            (ButtonText.HELP_SUBSCRIPTION, HelpSectionMode.SUBSCRIPTION),
        ],
        HelpSectionMode.QUERIES: [
            (ButtonText.HELP_QUERIES_DRUG_SEARCH, HelpSectionMode.QUERIES_DRUG_SEARCH),
            (ButtonText.HELP_QUERIES_PHARMA, HelpSectionMode.QUERIES_PHARMA_QUESTIONS),
            (ButtonText.HELP_QUERIES_QUESTIONS, HelpSectionMode.QUERIES_QUESTIONS),
        ],
        HelpSectionMode.TOKENS: [
            (ButtonText.HELP_TOKENS_FREE, HelpSectionMode.TOKENS_FREE)
        ]
    }

    # возврат Назад
    back_navigation = {
        HelpSectionMode.QUERIES: HelpSectionMode.MAIN,
        HelpSectionMode.TOKENS: HelpSectionMode.MAIN,
        HelpSectionMode.SUBSCRIPTION: HelpSectionMode.MAIN,
        HelpSectionMode.QUERIES_QUESTIONS: HelpSectionMode.QUERIES,
        HelpSectionMode.QUERIES_PHARMA_QUESTIONS: HelpSectionMode.QUERIES,
        HelpSectionMode.QUERIES_DRUG_SEARCH: HelpSectionMode.QUERIES,
        HelpSectionMode.TOKENS_FREE: HelpSectionMode.TOKENS
    }

    buttons: list[InlineKeyboardButton | list[InlineKeyboardButton]] = []
    if help_mode in menu_buttons:
        row_buttons: list = []
        for text, mode in menu_buttons[help_mode]:
            if help_mode == HelpSectionMode.SUBSCRIPTION:
                # все кнопки в одном ряду
                row_buttons = [InlineKeyboardButton(
                    text=text,
                    callback_data=HelpSectionCallback(mode=mode).pack()
                )]
                buttons.append(row_buttons)
            elif help_mode == HelpSectionMode.MAIN:
                buttons.append([InlineKeyboardButton(
                            text=text,
                            callback_data=HelpSectionCallback(mode=mode).pack()
                )])
                if len(row_buttons) > 1:
                    buttons.append(row_buttons.copy())
                    row_buttons.clear()
            else:
                # каждая кнопка в отдельном ряду
                buttons.append([InlineKeyboardButton(
                        text=text,
                        callback_data=HelpSectionCallback(mode=mode).pack()
                    )])

    if help_mode in back_navigation:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=ButtonText.LEFT_ARROW,
                    callback_data=HelpSectionCallback(
                        mode=back_navigation[help_mode]
                    ).pack()
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
