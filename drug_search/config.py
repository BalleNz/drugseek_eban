import logging
from os import environ, path
from pathlib import Path
from typing import ClassVar

from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from pydantic_settings import BaseSettings

# Получаем абсолютный путь к .env файлу
BASE_DIR = Path(__file__).parent.parent
ENV_PATH = path.join(BASE_DIR, '.env')

load_dotenv(ENV_PATH)

logger = logging.getLogger(__name__)


class Config(BaseSettings):
    """
    Singleton class for environ values.
    """
    # Режим разработки True/False
    DEBUG: ClassVar[bool] = environ.get("DEBUG", "true").lower() == "true"

    # Deepseek API
    DEEPSEEK_API_KEY: ClassVar[str] = environ.get("DEEPSEEK_API_KEY", "")
    MINIMUM_USD_ON_BALANCE: ClassVar[float] = 1

    # Database
    DATABASE_URL: str = environ.get("DATABASE_URL", "")

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: ClassVar[str] = environ.get("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_API_URL: ClassVar[str] = "https://api.telegram.org/bot"

    # FastAPI
    WEBAPP_HOST: str = environ.get("WEBAPP_HOST", "0.0.0.0")
    WEBAPP_PORT: int = int(environ.get("WEBAPP_PORT", "8000"))
    WEBHOOK_URL: str = environ.get("WEBHOOK_URL", "")  # Public URL like https://domain-name.ru/
    INTERNAL_API_URL: str = environ.get("INTERNAL_API_URL", "")  # Docker: http://fastapi:8000

    API_KEY: str = environ.get("API_KEY", "")

    # Yookassa
    PROVIDER_TOKEN: str = environ.get("PROVIDER_TOKEN", "")  # Токен платежки с BotFather
    CURRENCY: str = "RUB"

    # JWT
    SECRET_KEY: str = environ.get("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 1200

    # Redis
    REDIS_URL: str = environ.get("REDIS_URL", "redis://redis:6379")

    # ARQ
    ARQ_REDIS_URL: str = environ.get("ARQ_REDIS_URL", "")
    ARQ_REDIS_QUEUE: str = environ.get("ARQ_QUEUE", "arq:queue")
    ARQ_MAX_JOBS: int = int(environ.get("ARQ_MAX_JOBS", "10"))

    # AUTH ENDPOINT
    ACCESS_TOKEN_ENDPOINT: str = "v1/auth/"

    def __init__(self, **data):
        super().__init__(**data)

        if self.DEBUG:
            # Replace container addresses with localhost for development
            self.DATABASE_URL = self.DATABASE_URL.replace("db:", "localhost:")
            self.REDIS_URL = self.REDIS_URL.replace("redis://redis:", "redis://localhost:")
            self.ARQ_REDIS_URL = self.ARQ_REDIS_URL.replace("redis://redis:", "redis://localhost:")

        self._oauth2_scheme = OAuth2PasswordBearer(
            tokenUrl=self.ACCESS_TOKEN_ENDPOINT,
            scheme_name="TelegramAccessToken"
        )

    @property
    def OAUTH2_SCHEME(self):
        return self._oauth2_scheme

    @property
    def api_base_url(self) -> str:
        """URL for bot/worker → API calls inside Docker or locally."""
        if self.INTERNAL_API_URL:
            return self.INTERNAL_API_URL.rstrip("/")
        return self.WEBHOOK_URL.rstrip("/")

    @property
    def public_base_url(self) -> str:
        """Public HTTPS URL for WebApp links and external callbacks."""
        return self.WEBHOOK_URL.rstrip("/")


config: Config = Config()
logging.info(f"ENVIRONMENT CREATED: {config.model_dump()}")

if __name__ == "__main__":
    print(f"ENV_PATH: {ENV_PATH}")
    print(f"File exists: {path.exists(ENV_PATH)}")
    print(f"Config : {config.model_dump()}")
