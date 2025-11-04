from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from database.engine import clear_metadata_cache
from drug_search.config import config
from drug_search.core.app.main import fastapi_app
from drug_search.infrastructure.loggerConfig import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: очистка кеша метаданных при запуске
    await clear_metadata_cache()
    print("✓ Metadata cache cleared")

    yield  # Здесь приложение работает

    # Shutdown (опционально)
    print("Application shutting down")


# FASTAPI APP
app = fastapi_app
app.router.lifespan_context = lifespan

# TELEGRAM BOT
bot = ...

if __name__ == "__main__":
    configure_logging()
    uvicorn.run(
        app=fastapi_app,
        host=config.WEBAPP_HOST,
        port=config.WEBAPP_PORT,
    )
