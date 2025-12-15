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
    0: 2,  # key: reward (tokens)
    1: 6,
    2: 7,
    3: 10,
    4: 12,
    5: 15,
    6: 20,
    7: 25,
    8: 30,
    9: 35,
    10: 40,
    11: 50,
    12: 60,
    13: 70,
    14: 40,
    15: 50,
    16: 60,
    17: 50,
    18: 50,
    19: 60,
    20: 100,
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
    "zmtlk",
    "mybigmedicine"
)

FREE_TOKENS_AMOUNT = 7  # за подписки
