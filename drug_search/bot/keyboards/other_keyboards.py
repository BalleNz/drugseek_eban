import urllib.parse
import uuid

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButtonRequestChat

from drug_search.bot.keyboards import DrugDescribeCallback
from drug_search.bot.keyboards.callbacks import HelpSectionCallback, GetTokensForSubscriptionCallback, \
    ReferralsMenuCallback, \
    BuySubscriptionCallback, BuySubscriptionChosenTypeCallback
from drug_search.bot.lexicon.enums import HelpSectionMode
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.core.lexicon import ZMTLK_CHANNEL_USERNAME, SUBSCRIPTION_TYPES, DrugMenu
from keyboards.callbacks import InfoSectionCallback


def get_help_keyboard(
        help_mode: HelpSectionMode
):
    keyboard: InlineKeyboardMarkup

    menu_buttons = {
        HelpSectionMode.MAIN: [
            (ButtonText.HELP_TOKENS, HelpSectionMode.TOKENS),
            (ButtonText.HELP_SUBSCRIPTION, HelpSectionMode.SUBSCRIPTION),
        ],
        HelpSectionMode.TOKENS: [
            (ButtonText.HELP_TOKENS_FREE, HelpSectionMode.TOKENS_FREE)
        ]
    }

    # возврат Назад
    back_navigation = {
        HelpSectionMode.TOKENS: HelpSectionMode.MAIN,
        HelpSectionMode.SUBSCRIPTION: HelpSectionMode.MAIN,
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


def get_modes_information_keyboard() -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    for mode_text in (ButtonText.MODES_INFO_DRUG_SEARCH,
                      ButtonText.MODES_INFO_PHARMA,
                      ButtonText.MODES_INFO_QUESTIONS):
        buttons.append(
            [InlineKeyboardButton(
                text=mode_text,
                callback_data=InfoSectionCallback(
                    mode=mode_text
                ).pack()
            )]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


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


def check_subscription_condition() -> InlineKeyboardMarkup:
    """Клавиатура -> купить подписку или подписаться на канал"""
    DEEP_LINK = f"t.me/{ZMTLK_CHANNEL_USERNAME}"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Подписаться на канал",
                    url=DEEP_LINK
                )
            ],
            [
                InlineKeyboardButton(
                    text="Приобрести подписку",
                    callback_data=BuySubscriptionCallback().pack()
                )
            ]
        ]
    )


def referrals_menu_keyboard(
        url: str
) -> InlineKeyboardMarkup:
    request_chat = KeyboardButtonRequestChat(
        request_id=1,
        chat_is_channel=False,  # Только private/группы (не каналы) — для недавних диалогов
        chat_is_forum=False,  # Исключаем форумы
    )
    PREFILLED_TEXT = "\n\nПривет! Рекомендую тебе бота, который подскажет тебе за лекарства, которые ты принимаешь!"
    DEEP_LINK = f"https://t.me/share/url?url={url}&text={urllib.parse.quote(PREFILLED_TEXT, safe='')}"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Поделиться с друзьями",
                    url=DEEP_LINK,
                    request_chat=request_chat
                )
            ]
        ]
    )


def open_referrals_menu_keyboard() -> InlineKeyboardMarkup:
    """Открыть меню с рефералами (отправляется после /start)"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть реферальную систему",
                    callback_data=ReferralsMenuCallback().pack()
                )
            ]
        ]
    )


def get_subscription_packages_from_limitable_keyboard(
        user_subscription_type: SUBSCRIPTION_TYPES,
        drug_id: uuid.UUID,
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
                text=ButtonText.LEFT_ARROW,
                callback_data=DrugDescribeCallback(
                    drug_menu=DrugMenu.BRIEFLY,
                    drug_id=drug_id,
                ).pack()
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
