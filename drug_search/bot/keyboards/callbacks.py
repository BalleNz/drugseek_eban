import uuid
from enum import Enum
from typing import Optional

from aiogram.filters.callback_data import CallbackData


class DescribeTypes(str, Enum):
    DOSAGES = "Dosages"
    PATHWAYS = "Pathways"
    COMBINATIONS = "Combinations"
    RESEARCHES = "Researches"


class ArrowTypes(str, Enum):
    BACK = "back"
    FORWARD = "forward"


class DatabaseCallback(CallbackData, prefix="database"):
    ...


class DrugListCallback(CallbackData, prefix="drug_list"):
    arrow: Optional[ArrowTypes] = None
    page: int  # текущая страница


# Подробное описание препарата
class DrugDescribeCallback(CallbackData, prefix="drug_describe"):
    drug_id: uuid.UUID
    briefly: bool
    describe_type: Optional[DescribeTypes]
