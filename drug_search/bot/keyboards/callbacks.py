import uuid

from aiogram.filters.callback_data import CallbackData

DESCRIBE_TYPES = [
    "Dosages",
    "Pathways",
    "Combinations",
    "Researches"
]

ARROW_TYPES = [
    "back",
    "forward"
]


class DatabaseCallback(CallbackData, prefix="database"):
    ...


class DrugDatabaseScrollingCallback(CallbackData, prefix="database_arrows"):
    arrow: ARROW_TYPES
    page: int  # текущая страница


class DrugBrieflyCallback(CallbackData, prefix="drug_briefly"):
    drug_id: uuid.UUID


# Подробное описание препарата
class DrugDescribeCallback(CallbackData, prefix="drug_describe"):
    drug_id: uuid.UUID
    describe_type: DESCRIBE_TYPES
