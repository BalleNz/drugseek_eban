from drug_search.core.lexicon.consts import *
from drug_search.core.lexicon.enums import *
from drug_search.core.lexicon.prompts import Prompts

__all__ = [
    "Prompts",
    # [ Enums ]
    'SUBSCRIBE_TYPES',
    'DANGER_CLASSIFICATION',
    'EXIST_STATUS',
    'ACTIONS_FROM_ASSISTANT',
    'ARROW_TYPES',
    'JobStatuses',
    'MailingStatuses',
    # [ Limits ]
    'QUESTIONS_LIMIT_START',
    'DEFAULT_SEARCH_DAY_LIMIT',
    'DEFAULT_QUESTIONS_DAY_LIMIT',
    'LITE_QUESTIONS_DAY_LIMIT',
    'LITE_SEARCH_DAY_LIMIT',
    'PREMIUM_SEARCH_DAY_LIMIT',
    'PREMIUM_QUESTIONS_DAY_LIMIT',
    # [ Message limits ]
    'ANTISPAM_DEFAULT',
    'ANTISPAM_LITE',
    'ANTISPAM_PREMIUM',
    'MAX_MESSAGE_LENGTH_DEFAULT',
    # [ CONSTS ]
    'UPDATE_DRUG_COST',
    'ADMINS_TG_ID',
    'ASSISTANT_ANSWER_DRUG_COUNT_PER_PAGE'
]
