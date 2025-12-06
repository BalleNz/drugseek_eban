import logging
import uuid

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from drug_search.bot.keyboards import (DrugDescribeCallback, DrugListCallback, WrongDrugFoundedCallback)
from drug_search.bot.keyboards.callbacks import (AssistantQuestionContinueCallback, DrugUpdateRequestCallback,
                                                 UserDescriptionCallback, HelpSectionCallback,
                                                 BuyDrugRequestCallback, BackToUserProfileCallback,
                                                 BuySubscriptionCallback, BuyTokensCallback,
                                                 BuyTokensConfirmationCallback, BuySubscriptionChosenTypeCallback,
                                                 DrugDescribeResearchesCallback, BuySubscriptionConfirmationCallback,
                                                 SimpleModeProfileCallback, GetTokensForSubscriptionCallback,
                                                 ReferralsMenuCallback)
from drug_search.bot.lexicon.enums import ModeTypes, HelpSectionMode
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.core.lexicon import (ARROW_TYPES, TokenPackage, SubscriptionPackage,
                                      SUBSCRIPTION_TYPES)
from drug_search.core.lexicon.enums import DrugMenu
from drug_search.core.schemas import DrugBrieflySchema, DrugSchema, UserSchema, DrugResearchSchema
from drug_search.core.utils.funcs import may_update_drug

logger = logging.getLogger(__name__)

# [Reply]
menu_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=ButtonText.DRUG_DATABASE)],
        [KeyboardButton(text=ButtonText.PROFILE)],
        [KeyboardButton(text=ButtonText.HELP)],
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

    total_pages = len(researches) // page_size

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


# [ USER PROFILE ]
def user_profile_keyboard(
        user: UserSchema
) -> InlineKeyboardMarkup:
    """
    Кнопки:
    — Описание
    — Подписка (Купить / Улучшить)
    """
    subscription_text = None
    if user.subscription_type == SUBSCRIPTION_TYPES.LITE:
        subscription_text = ButtonText.UPGRADE_SUBSCRIPTION
    elif user.subscription_type == SUBSCRIPTION_TYPES.DEFAULT:
        subscription_text = ButtonText.BUY_SUBSCRIPTION

    buttons: list[list[InlineKeyboardButton]] = [[]]

    if user.subscription_type != SUBSCRIPTION_TYPES.PREMIUM:
        buttons.append([
            InlineKeyboardButton(
                text=subscription_text,
                callback_data=BuySubscriptionCallback().pack(),
            )]
        )

    if user.description:
        buttons.append([
            InlineKeyboardButton(
                text=ButtonText.SHOW_DESCRIPTION,
                callback_data=UserDescriptionCallback().pack()
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text=ButtonText.BUY_TOKENS,
            callback_data=BuyTokensCallback().pack()
        )
    ])

    buttons.append([
        InlineKeyboardButton(
            text=ButtonText.SIMPLE_MODE_ON if user.simple_mode else ButtonText.SIMPLE_MODE_OFF,
            callback_data=SimpleModeProfileCallback().pack()
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


def back_to_user_profile() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ButtonText.LEFT_ARROW,
                    callback_data=BackToUserProfileCallback().pack()
                )
            ]
        ]
    )


# [ PAYMENT ]
def get_tokens_packages_to_buy_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с пакетами токенов"""

    buttons: list[list[InlineKeyboardButton]] = []

    for token_package in TokenPackage.get_token_packages():
        buttons.append([
            InlineKeyboardButton(
                text=token_package.name + f" ({int(token_package.price)} рублей)",
                callback_data=BuyTokensConfirmationCallback(
                    token_package_key=token_package.key
                ).pack()
            )
        ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


def get_subscription_packages_types_keyboard(
        user_subscription_type: SUBSCRIPTION_TYPES
) -> InlineKeyboardMarkup:
    """клавиатура с пакетами подписок в зависимости от текущей подписки пользователя"""
    buttons = []

    if user_subscription_type in [SUBSCRIPTION_TYPES.DEFAULT]:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="⚡ Лайт",
                    callback_data=BuySubscriptionChosenTypeCallback(
                        subscription_type=SUBSCRIPTION_TYPES.LITE
                    ).pack()
                )
            ]
        )

    if user_subscription_type in [SUBSCRIPTION_TYPES.DEFAULT, SUBSCRIPTION_TYPES.LITE]:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="💎️ Премиум",
                    callback_data=BuySubscriptionChosenTypeCallback(
                        subscription_type=SUBSCRIPTION_TYPES.PREMIUM
                    ).pack()
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=BackToUserProfileCallback().pack()
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


def get_subscription_packages_keyboard(
        chosen_subscription_type: SUBSCRIPTION_TYPES,
        user_subscription_type: SUBSCRIPTION_TYPES,
        subscription_days: int | None
) -> InlineKeyboardMarkup:
    """клавиатура с выбором пакетов подписок"""

    subscription_packages: tuple[SubscriptionPackage, ...] = SubscriptionPackage.get_packages_by_type(
        chosen_subscription_type)

    buttons: list[list[InlineKeyboardButton]] = [[]]

    for package in subscription_packages:
        buttons.append([
            InlineKeyboardButton(
                text=package.name + f" ({package.price(subscription_days)} рублей)",
                callback_data=BuySubscriptionConfirmationCallback(
                    subscription_package_key=package.key
                ).pack()
            )]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=BuySubscriptionCallback().pack()
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


def get_url_to_buy_keyboard(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Перейти в покупке",
                    url=url
                )
            ]
        ]
    )


# [ HELP ]
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


# [ REFERRALS ]
def get_free_tokens_menu_keyboard(
        got_free_tokens: bool
):
    """Клавиатура с кнопками:
    — Токены бесплатно (единоразово)
    — Токены за подписку
    """
    buttons: list[list[InlineKeyboardButton]] = []

    if not got_free_tokens:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Токены за подписку",
                    callback_data=GetTokensForSubscriptionCallback().pack()
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="Реферальная система",
                callback_data=ReferralsMenuCallback().pack()
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


def get_tokens_for_subscription_channel_list(
        channels_username_check: list[tuple[str, str]]
) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    for i, channel_info in enumerate(channels_username_check, start=1):
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{i} Канал {"✅" if channel_info[1] else "❌"}",
                    url=f"https://t.me/{channel_info[0]}"
                )
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text=f"Проверить подписки",
                callback_data=GetTokensForSubscriptionCallback().pack()
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


def referrals_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Обновить страницу",
                    callback_data=ReferralsMenuCallback().pack()
                )
            ]
        ]
    )
