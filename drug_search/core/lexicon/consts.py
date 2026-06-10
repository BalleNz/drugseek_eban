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
MAX_MESSAGE_LENGTH_DEFAULT = 100  # символов
MAX_MESSAGE_LENGTH_LITE = 500
MAX_MESSAGE_LENGTH_PREMIUM = 2000

# [ BOT ]
BOT_USERNAME = "drugseek_bot"
MARKETING_CHANNEL_USERNAME = "drugseeks"

WEEKLY_DRUG_FOOTER = (
    "\n\n—\n"
    "А разобрать любой препарат вы можете в моём боте @{bot_username}"
)

# [ REFERRALS ]
REFERRALS_REWARDS = {
    0: 1,  # key: reward (tokens)
    1: 2,
    2: 3,
    3: 3,
    4: 3,
    5: 4,
    6: 7,
    7: 15,
    8: 15,
    9: 15,
    10: 22,
    11: 22,
    12: 33,
    13: 33,
    14: 40,
    15: 50,
    16: 60,
    17: 50,
    18: 50,
    19: 60,
    20: 100,
}

REFERRALS_LEVELS = {
    0: 2,  # level: referrals need
    1: 4,
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
    12: 170,
    13: 190,
    14: 250,
    15: 300,
    16: 400,
    17: 500,
    18: 600,
    19: 700,
    20: 800,
}

# [ CHANNELS ]
ZMTLK_CHANNEL_USERNAME = f"zmtlk"

# [ BONUSES ]
CHANNELS_USERNAME_FREE_TOKENS = (
    "drugseeks",
    "zmtlk"
)

FREE_TOKENS_AMOUNT = 3  # за подписки
