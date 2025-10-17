from enum import Enum


class ModeTypes(str, Enum):
    SEARCH = "search"
    DATABASE = "database"
    WRONG_DRUG = "wrong_drug"
