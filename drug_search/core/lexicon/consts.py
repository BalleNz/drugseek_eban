# [платежные пакеты для запросов]
SMALL_PACKET: int = 10
BASIC_PACKET: int = 25
PRO_PACKET: int = 50
ENTERPRISE_PACKET: int = 70
ULTIMATE_PACKET: int = 200

# [ API rules ]
MIN_DAYS_TO_UPDATE_DRUG: int = 60

# [ COSTS ]
NEW_DRUG_COST: int = 2
UPDATE_DRUG_COST: int = 1

QUESTION_COST: int = 1

# [ VARIABLES ]
ASSISTANT_ANSWER_DRUG_COUNT_PER_PAGE: int = 3

# [ ADMIN ]
ADMINS_TG_ID = [
    "1257313065"
]

# [ MESSAGE ANTI_SPAM ]
ANTISPAM_DEFAULT = {
    "max_requests": 2,
    "time_limit": 60
}
ANTISPAM_LITE = {
    "max_requests": 5,
    "time_limit": 60
}

# [ LIMITS ]
MAX_MESSAGE_LENGTH_DEFAULT = 30  # символов
MAX_MESSAGE_LENGTH_LITE = 70
MAX_MESSAGE_LENGTH_PREMIUM = 400
