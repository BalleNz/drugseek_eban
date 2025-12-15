import uuid

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from drug_search.bot.keyboards import DrugDescribeCallback, DrugListCallback, WrongDrugFoundedCallback
from drug_search.bot.keyboards.callbacks import DrugDescribeResearchesCallback, DrugUpdateRequestCallback, \
    BuyDrugRequestCallback, \
    AssistantQuestionContinueCallback
from drug_search.bot.keyboards.menu_markup import logger
from drug_search.bot.lexicon.enums import ModeTypes
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.core.lexicon import DrugMenu, ARROW_TYPES, SUBSCRIPTION_TYPES
from drug_search.core.schemas import DrugBrieflySchema, DrugResearchSchema, DrugSchema
from drug_search.core.utils.funcs import may_update_drug


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
                        drug_menu=DrugMenu.BRIEFLY,
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


def drug_researches_keyboard(
        researches: list[DrugResearchSchema],
        drug_id: uuid.UUID,
        current_page_number: int,
        research_number: int = 0,
) -> InlineKeyboardMarkup:
    """Клавиатура для листинга исследований"""

    page_size = 4

    # [ текущая страница ]
    # изначально может быть отлИчной от той, в которой сейчас находится исследование
    logger.info(f"Current_page_number: {current_page_number}")

    current_start_index = current_page_number * page_size

    current_page = researches[current_start_index:current_start_index + page_size]

    buttons: list[InlineKeyboardButton] = []
    for i, research in enumerate(current_page):
        current_research_number: int = i + (current_page_number * page_size)

        buttons.append(
            InlineKeyboardButton(
                text=research.header if current_research_number != research_number else f"| {research.header} |",
                callback_data=DrugDescribeResearchesCallback(
                    drug_id=drug_id,
                    research_number=current_research_number,
                    current_page_number=current_page_number
                ).pack()
            )
        )

    total_pages = (len(researches) // page_size) - 1

    buttons_arrows: list[InlineKeyboardButton] = []

    if current_page_number > 0:
        buttons_arrows.append(
            InlineKeyboardButton(
                text="<——",
                callback_data=DrugDescribeResearchesCallback(
                    drug_id=drug_id,
                    research_number=research_number,
                    current_page_number=current_page_number - 1
                ).pack()
            )
        )

    if current_page_number < total_pages:
        buttons_arrows.append(
            InlineKeyboardButton(
                text="——>",
                callback_data=DrugDescribeResearchesCallback(
                    drug_id=drug_id,
                    research_number=research_number,
                    current_page_number=current_page_number + 1
                ).pack()
            )
        )

    return_to_menu_button = InlineKeyboardButton(
        text="Вернуться в меню",
        callback_data=DrugDescribeCallback(
            drug_id=drug_id,
            drug_menu=DrugMenu.BRIEFLY
        ).pack()
    )

    keyboard = []

    for button in buttons:
        keyboard.append([button])

    # Добавляем стрелки навигации в одну строку (если есть)
    if buttons_arrows:
        keyboard.append(buttons_arrows)

    # Добавляем кнопку возврата в меню в отдельную строку
    keyboard.append([return_to_menu_button])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def drug_keyboard(
        drug: DrugSchema,
        drug_menu: DrugMenu,
        user_subscribe_type: SUBSCRIPTION_TYPES | None,
        mode: ModeTypes,
        page: int | None = None,  # страница с прошлого меню
        user_query: str | None = None
) -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру по describe_type:
    а) с выбором разделов препарата,
    б) со стрелкой возвращения в меню листинг
    """
    if drug_menu != DrugMenu.BRIEFLY:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=ButtonText.LEFT_ARROW,
                        callback_data=DrugDescribeCallback(
                            drug_menu=DrugMenu.BRIEFLY,
                            drug_id=drug.id,
                            page=page
                        ).pack()
                    )
                ]
            ]
        )
        if drug_menu == DrugMenu.UPDATE_INFO:
            # [ обновить препарат ]
            if user_subscribe_type != SUBSCRIPTION_TYPES.PREMIUM:
                update_text = ButtonText.UPDATE_DRUG
            else:
                update_text = ButtonText.UPDATE_DRUG_FOR_PREMIUM

            keyboard.inline_keyboard.insert(
                0,
                [
                    InlineKeyboardButton(
                        text=update_text,
                        callback_data=DrugUpdateRequestCallback(
                            drug_id=drug.id
                        ).pack()
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
                        drug_menu=DrugMenu.DOSAGES,
                        drug_id=drug.id,
                        page=page
                    ).pack()
                ),
                InlineKeyboardButton(
                    text=ButtonText.METABOLISM,
                    callback_data=DrugDescribeCallback(
                        drug_menu=DrugMenu.METABOLISM,
                        drug_id=drug.id,
                        page=page
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=ButtonText.COMBINATIONS,
                    callback_data=DrugDescribeCallback(
                        drug_menu=DrugMenu.COMBINATIONS,
                        drug_id=drug.id,
                        page=page
                    ).pack()
                ),
                InlineKeyboardButton(
                    text=ButtonText.ANALOGS,
                    callback_data=DrugDescribeCallback(
                        drug_menu=DrugMenu.ANALOGS,
                        drug_id=drug.id,
                        page=page
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=ButtonText.MECHANISM,
                    callback_data=DrugDescribeCallback(
                        drug_menu=DrugMenu.MECHANISM,
                        drug_id=drug.id,
                        page=page
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=ButtonText.RESEARCHES,
                    callback_data=DrugDescribeResearchesCallback(
                        drug_id=drug.id,
                        research_number=0,
                        current_page_number=0
                    ).pack()
                )
            ],
        ]
    )

    if mode == ModeTypes.DATABASE and may_update_drug(drug.updated_at) and drug_menu == DrugMenu.BRIEFLY:
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=ButtonText.UPDATE_DRUG,
                    callback_data=DrugDescribeCallback(
                        drug_menu=drug_menu.UPDATE_INFO,
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
                    callback_data=AssistantQuestionContinueCallback(
                        question=question,
                        arrow=arrow
                    ).pack()
                )
            ]
        ]
    )
