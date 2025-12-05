from drug_search.core.lexicon.consts import *
from drug_search.core.lexicon.enums import *
from drug_search.core.lexicon.prompts import Prompts

__all__ = [
    "Prompts",
    # [ Enums ]
    'DANGER_CLASSIFICATION',
    'EXIST_STATUS',
    'ACTIONS_FROM_ASSISTANT',
    'ARROW_TYPES',
    'JobStatuses',
    'MailingStatuses',
    'TokenPackage',
    'SubscriptionPackage',
    'SUBSCRIPTION_TYPES',
    'SMALL_PACKET',
    'ENTERPRISE_PACKET',
    'ULTIMATE_PACKET',
    'PRO_PACKET',
    'BASIC_PACKET',
    # [ Limits ]
    'TOKENS_LIMIT',
    # [ Message limits ]
    'ANTISPAM_DEFAULT',
    'ANTISPAM_LITE',
    'MAX_MESSAGE_LENGTH_DEFAULT',
    'MAX_MESSAGE_LENGTH_LITE',
    'MAX_MESSAGE_LENGTH_PREMIUM',
    # [ CONSTS ]
    'UPDATE_DRUG_COST',
    'ADMINS_TG_ID',
    'ASSISTANT_ANSWER_DRUG_COUNT_PER_PAGE',
    'NEW_DRUG_COST',
    'QUESTION_COST',
    'REFERRALS_REWARDS',
    'BOT_USERNAME',
    'REFERRALS_LEVELS',
    'FREE_TOKENS_AMOUNT'
]
