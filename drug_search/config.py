from os import environ
from typing import ClassVar

from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    """
    Singleton class for environ values.
    """
    # TOKEN SYSTEM
    NEW_DRUG_COST: int = 1  # allow or generate drug to user

    # Режим разработки True/False
    DEBUG_MODE: ClassVar[bool] = True

    # Deepseek API
    DEEPSEEK_API_KEY: ClassVar[str] = environ.get("DEEPSEEK_API_KEY", "")

    # Database
    DATABASE_URL: ClassVar[str] = environ.get("DATABASE_URL", "")
    DATABASE_TEST_URL: ClassVar[str] = environ.get("DATABASE_URL_TEST", "")

    # Telegram Bot
    BOT_TOKEN: ClassVar[str]

    # FastAPI
    WEBAPP_HOST: str = environ.get("WEBAPP_HOST", "0.0.0.0")
    WEBAPP_PORT: int = int(environ.get("WEBAPP_PORT", "8000"))
    WEBHOOK_URL: str = environ.get("WEBHOOK_URL", "")  # URL like https://domain-name.ru/

    # JWT
    SECRET_KEY: str = "zallopppaaa"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 1200

    # Redis
    REDIS_URL: str = environ.get("REDIS_URL", "redis_pool://localhost:6379/0")


    # AUTH ENDPOINT
    ACCESS_TOKEN_ENDPOINT: str = "v1/auth/"

    def __init__(self, **data):
        super().__init__(**data)
        self._oauth2_scheme = OAuth2PasswordBearer(
            tokenUrl=self.ACCESS_TOKEN_ENDPOINT,
            scheme_name="TelegramAccessToken"
        )

    @property
    def OAUTH2_SCHEME(self):
        return self._oauth2_scheme


config: Config = Config()
