from enum import Enum


class ACTIONS_FROM_ASSISTANT(str, Enum):
    DRUG_SEARCH = "drug_search"
    QUESTION = "question"
    SPAM = "spam"  # будет давать предупреждение, в случае повтора даст мут
    OTHER = "other"


class EXIST_STATUS(Enum):
    EXIST: str = "exist"
    NOT_EXIST: str = "not exist"


class DANGER_CLASSIFICATION(Enum):
    SAFE: str = "SAFE"
    SUBSCRIPTION_NEED: str = "SUBSCRIPTION_NEED"
    DANGER: str = "DANGER"
