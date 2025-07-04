from dotenv import dotenv_values

env = dotenv_values("../.env")


class Config:
    DEBUG_MODE: bool = True

    # DATABASE SETTINGS
    DATABASE_URL: str = env.get("DATABASE_URL", "")
    DATABASE_URL_TEST: str = DATABASE_URL + "_test"

    # BOT SETTINGS
    ...


config = Config()
