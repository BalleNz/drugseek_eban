from os import environ
from typing import ClassVar

from dotenv import load_dotenv
from pydantic import BaseSettings, ConfigDict

load_dotenv()


class Config(BaseSettings):
    """
    Singleton class for environ values.
    """
    # Режим разработки True/False
    DEBUG_MODE: ClassVar[bool] = True

    # Deepseek API
    DEEPSEEK_API_KEY: ClassVar[str] = environ.get("DEEPSEEK_API_KEY", "")

    # Database
    DATABASE_URL: ClassVar[str] = environ.get("DATABASE_URL", "")

    # Telegram Bot
    BOT_TOKEN: ClassVar[str]

    # FastAPI
    WEBAPP_HOST: str = environ.get("WEBAPP_HOST", "0.0.0.0")  # Для Docker
    WEBAPP_PORT: int = int(environ.get("WEBAPP_PORT", "8000"))
    WEBHOOK_URL: str = environ.get("WEBHOOK_URL")  # Полный URL для вебхуков (если используется)

    # Redis (для хранения временных данных или кеша)
    REDIS_URL: str = environ.get("REDIS_URL", "redis://localhost:6379/0")

    #
    

config = Config()
