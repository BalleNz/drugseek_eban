import uuid
from typing import Optional

from aiogram.filters.callback_data import CallbackData

from drug_search.bot.lexicon.enums import HelpSectionMode, DrugMenu
from drug_search.core.lexicon.enums import ARROW_TYPES, SUBSCRIPTION_TYPES


# [ CALLBACKS ]
# [ база данных ]
class DatabaseCallback(CallbackData, prefix="database"):
    pass


class DrugListCallback(CallbackData, prefix="drug_list"):
    arrow: Optional[ARROW_TYPES] = None
    page: int  # текущая страница


# [ drug_actions ]
class DrugUpdateRequestCallback(CallbackData, prefix="drug_update"):
    """Обновление препарата"""
    drug_id: uuid.UUID


class DrugResearchesUpdateCallback(CallbackData, prefix="drug_researches_update"):
    """Обновление исследований препарата"""
    drug_id: uuid.UUID


class DrugDescribeResearchesCallback(CallbackData, prefix="drug_researches"):
    """Описание исследований"""
    drug_id: uuid.UUID
    research_number: int
    current_page_number: int


class DrugDescribeCallback(CallbackData, prefix="drug_describe"):
    # Подробное описание препарата
    drug_id: uuid.UUID
    drug_menu: Optional[DrugMenu]
    page: int | None = None  # страница с прошлого меню | None (если вне меню)


# [ ACTIONS ]
class WrongDrugFoundedCallback(CallbackData, prefix="wrong_drug"):
    # если найден неверный препарат
    drug_name_query: str


class AssistantQuestionContinueCallback(CallbackData, prefix="quest_cont"):
    question: str
    arrow: ARROW_TYPES


# [ покупка препарата ]
class BuyDrugRequestCallback(CallbackData, prefix="buy_drug"):
    pass


class CancelDrugBuyingCallback(CallbackData, prefix="cancel_buying_drug"):
    pass


# [ USER PROFILE ]
class UserDescriptionCallback(CallbackData, prefix="user_description"):
    pass


class BackToUserProfileCallback(CallbackData, prefix="back_to_profile"):
    pass


# [ PAYMENT ]

class BuySubscriptionCallback(CallbackData, prefix="buy_subscription"):
    """Клик на 'Купить подписку' | 'Улучшить подписку' из Профиля"""
    pass


class BuySubscriptionChosenTypeCallback(CallbackData, prefix="buy_subscription"):
    """Клик на выбор типа подписки"""
    subscription_type: SUBSCRIPTION_TYPES


class BuySubscriptionConfirmationCallback(CallbackData, prefix="buy_subscription_conf"):
    """Клик на выбор пакета подписки"""
    subscription_package_key: str


class BuyTokensCallback(CallbackData, prefix="buy_tokens"):
    """Клик на 'Купить токены' из Профиля"""
    pass


class BuyTokensConfirmationCallback(CallbackData, prefix="buy_tokens_conf"):
    """Клик на выбор пакета токенов"""
    token_package_key: str


class FinishPaymentCallback(CallbackData, prefix="finish_buying"):
    """После перехода по ссылке для оплаты"""
    pass


# [ HELP ]

class HelpSectionCallback(CallbackData, prefix="help"):
    mode: HelpSectionMode
