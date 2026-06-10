from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from drug_search.bot.keyboards.callbacks import BuyTokensConfirmationCallback, BuySubscriptionChosenTypeCallback, \
    BackToUserProfileCallback, BuySubscriptionConfirmationCallback, BuySubscriptionCallback, \
    BuyDrugPackConfirmationCallback
from drug_search.core.lexicon import TokensPackage, SUBSCRIPTION_TYPES, SubscriptionPackage, SubscriptionKeys, \
    DrugPackPackage


def get_tokens_packages_to_buy_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с пакетами токенов"""

    buttons: list[list[InlineKeyboardButton]] = []

    for token_package in TokensPackage.get_token_packages():
        emoji = ""
        match token_package.key:
            case "business":
                emoji = "⚡ "
            case "maximum":
                emoji = "🔥 "

        buttons.append([
            InlineKeyboardButton(
                text=emoji + token_package.name + f" ({int(token_package.price)} рублей) {emoji}",
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
        subscription_days: int | None
) -> InlineKeyboardMarkup:
    """клавиатура с выбором пакетов подписок"""

    subscription_packages: tuple[SubscriptionPackage, ...] = SubscriptionPackage.get_packages_by_type(
        chosen_subscription_type)

    buttons: list[list[InlineKeyboardButton]] = [[]]

    for package in subscription_packages:
        emoji = ""
        match package.key:
            case SubscriptionKeys.TWO_WEEKS_LITE:
                emoji = "⚡ "
            case SubscriptionKeys.THREE_MONTHS_PREMIUM:
                emoji = "⚡ "
            case SubscriptionKeys.YEAR_PREMIUM:
                emoji = "💎 "

        buttons.append([
            InlineKeyboardButton(
                text=emoji + package.name + f" ({package.price(subscription_days)} рублей) {emoji}",
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


def get_drug_packs_keyboard() -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []

    emoji_map = {
        "pack_pharma": "💊 ",
        "pack_steroid": "💪 ",
        "pack_prohibited": "🚫 ",
        "pack_complex": "🔥 ",
    }

    for pack in DrugPackPackage.get_all_packs():
        emoji = emoji_map.get(pack.key, "")
        buttons.append([
            InlineKeyboardButton(
                text=f"{emoji}{pack.name} ({pack.price} ₽)",
                callback_data=BuyDrugPackConfirmationCallback(pack_key=pack.key).pack(),
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="Назад",
            callback_data=BackToUserProfileCallback().pack(),
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
