from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from drug_search.bot.keyboards.callbacks import BuySubscriptionCallback, UserDescriptionCallback, BuyTokensCallback, \
    SimpleModeProfileCallback, BackToUserProfileCallback, BuyDrugPackCallback
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.core.lexicon import SUBSCRIPTION_TYPES
from drug_search.core.schemas import UserSchema


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
            text=ButtonText.BUY_DRUG_PACKS,
            callback_data=BuyDrugPackCallback().pack()
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
