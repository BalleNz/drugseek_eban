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

# [ BOT ]
BOT_USERNAME = "drugseek_bot"

# [ REFERRALS ]
REFERRALS_REWARDS = {
    0: 3,  # key: reward (tokens)
    1: 7,
    2: 15,
    3: 20,
    4: 30,
    5: 40,
    6: 50,
    7: 60,
    8: 70,
    9: 80,
    10: 90,
    11: 100,
    12: 100,
    13: 110,
    14: 120,
    15: 130,
    16: 140,
    17: 200,
    18: 300,
    19: 400,
    20: 500,
}

REFERRALS_LEVELS = {
    0: 1,  # level: referrals need
    1: 2,
    2: 5,
    3: 10,
    4: 15,
    5: 20,
    6: 30,
    7: 40,
    8: 60,
    9: 90,
    10: 130,
    11: 150,
    12: 200,
    13: 250,
    14: 300,
    15: 500,
    16: 1000,
    17: 2000,
    18: 5000,
    19: 10000,
    20: 100000,
}


# [ BONUSES ]
CHANNELS_USERNAME_FREE_TOKENS = (
    "drugseeks",
    "zmtlk",
)

FREE_TOKENS_AMOUNT = 10  # за подписки
