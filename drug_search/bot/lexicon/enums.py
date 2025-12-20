from enum import Enum

from lexicon.keyboard_words import ButtonText


class ModeTypes(str, Enum):
    SEARCH = "search"
    DATABASE = "database"
    WRONG_DRUG = "wrong_drug"


class HelpSectionMode(str, Enum):
    # [ MAIN ]
    MAIN = "main"

    # [ TOKENS ]
    TOKENS = "tokens"
    TOKENS_FREE = "tokens_free"  # отсылает в команды /referrals | /free_tokens

    # [ SUBSCRIPTION ]
    SUBSCRIPTION = "subscription"
