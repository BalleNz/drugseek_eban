import uuid
from enum import Enum
from typing import Optional

from aiogram.filters.callback_data import CallbackData

from drug_search.bot.lexicon.enums import UserDescriptionMode, HelpSectionMode
from drug_search.core.lexicon.enums import ARROW_TYPES


# [ TYPES ]
class DescribeTypes(str, Enum):
    BRIEFLY = "Briefly"
    DOSAGES = "Dosages"
    MECHANISM = "Mechanism"
    COMBINATIONS = "Combinations"
    RESEARCHES = "Researches"
    ANALOGS = "Analogs"
    METABOLISM = "Metabolism"
    UPDATE_INFO = "UpdateInfo"


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


class DrugDescribeCallback(CallbackData, prefix="drug_describe"):
    # Подробное описание препарата
    drug_id: uuid.UUID
    describe_type: Optional[DescribeTypes]
    page: int | None  # страница с прошлого меню | None (если вне меню)


# [ ACTIONS ]
class WrongDrugFoundedCallback(CallbackData, prefix="wrong_drug"):
    # если найден неверный препарат
    drug_name_query: str


class AssistantQuestionContinue(CallbackData, prefix="quest_cont"):
    question: str
    arrow: ARROW_TYPES


# [ покупка препарата ]
class BuyDrugRequestCallback(CallbackData, prefix="buy_drug"):
    pass


class CancelDrugBuyingCallback(CallbackData, prefix="cancel_buying_drug"):
    pass


# [ USER PROFILE ]
class UserDescriptionCallback(CallbackData, prefix="user_description"):
    mode: UserDescriptionMode


# [ HELP ]
class HelpSectionCallback(CallbackData, prefix="help"):
    mode: HelpSectionMode
