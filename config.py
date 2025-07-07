from os import environ

from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Singleton class for environ values.
    """
    DEBUG_MODE: bool = True

    # DEEPSEEK API
    DEEPSEEK_API_KEY: str = environ.get("DEEPSEEK_API_KEY", "")

    # DATABASE SETTINGS
    DATABASE_URL: str = environ.get("DATABASE_URL", "")
    DATABASE_URL_TEST: str = DATABASE_URL + "_test"

    # BOT SETTINGS
    ...


config = Config()
