import asyncio
import logging

import aiogram
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from drug_search.core.dependencies.redis_service_dep import redis_client
from drug_search.bot.handlers.start import router as start_router
from drug_search.bot.handlers.database import router as database_router
from drug_search.bot.handlers.profile import router as profile_router
from drug_search.bot.handlers.main import router as actions_router
from drug_search.bot.handlers.actions import router as drug_actions_router
from drug_search.bot.middlewares.depends_injectors import DependencyInjectionMiddleware
from drug_search.config import config


def setup_auth(dp: Dispatcher):
    # Регистрация middleware
    dp.update.outer_middleware(DependencyInjectionMiddleware())

    # Регистрация хендлеров (порядок важен)
    for router in [
        start_router,
        database_router,
        profile_router,
        actions_router,
        drug_actions_router
    ]:
        dp.include_router(router)


async def start_polling(dp: Dispatcher):
    await dp.start_polling(bot)


storage = RedisStorage(redis_client)
dp = Dispatcher(storage=storage)

bot = aiogram.Bot(
    token=config.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

if __name__ == "__main__":
    setup_auth(dp)
    asyncio.run(start_polling(dp))
