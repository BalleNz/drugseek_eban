from enum import Enum


class ACTIONS_FROM_ASSISTANT(str, Enum):
    DRUG_SEARCH = "drug_search"
    QUESTION = "question"
    SPAM = "spam"  # будет давать предупреждение, в случае повтора даст мут
    OTHER = "other"
