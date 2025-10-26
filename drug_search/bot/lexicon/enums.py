from enum import Enum


class ModeTypes(str, Enum):
    SEARCH = "search"
    DATABASE = "database"
    WRONG_DRUG = "wrong_drug"


class UserDescriptionMode(str, Enum):
    SHOW_DESCRIPTION = "show_description"
    BACK_TO_PROFILE = "back_to_profile"


class HelpSectionMode(str, Enum):
    # [ MAIN ]
    MAIN = "main"

    # [ QUERIES ]
    QUERIES = "queries"
    QUERIES_QUESTIONS = "queries_questions"
    QUERIES_PHARMA_QUESTIONS = "queries_pharma_questions"
    QUERIES_DRUG_SEARCH = "queries_drug_search"

    # [ TOKENS ]
    TOKENS = "tokens"
    TOKENS_FREE = "tokens_free"  # отсылает в команды /referrals | /free_tokens

    # [ SUBSCRIPTION ]
    SUBSCRIPTION = "subscription"
