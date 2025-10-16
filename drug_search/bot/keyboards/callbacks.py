import uuid
from enum import Enum
from typing import Optional

from aiogram.filters.callback_data import CallbackData

from drug_search.core.lexicon.enums import DANGER_CLASSIFICATION
from drug_search.core.schemas import DrugAnswer


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


class ArrowTypes(str, Enum):
    BACK = "back"
    FORWARD = "forward"


# [ CALLBACKS ]
# [ база данных ]
class DatabaseCallback(CallbackData, prefix="database"):
    pass


class DrugListCallback(CallbackData, prefix="drug_list"):
    arrow: Optional[ArrowTypes] = None
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
    arrow: ArrowTypes


# [ покупка препарата ]
class BuyDrugRequestCallback(CallbackData, prefix="buy_drug"):
    drug_name: str  # если нужно предварительно создать
    drug_id: uuid.UUID | None  # если есть в БД
    danger_classification: DANGER_CLASSIFICATION


class CancelDrugBuyingCallback(CallbackData, prefix="cancel_buying_drug"):
    pass
