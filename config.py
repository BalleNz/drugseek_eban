from os import environ

from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG_MODE: bool = True

    # DATABASE SETTINGS
    DATABASE_URL: str = environ.get("DATABASE_URL", "")
    DATABASE_URL_TEST: str = DATABASE_URL + "_test"

    # BOT SETTINGS
    ...


config = Config()
