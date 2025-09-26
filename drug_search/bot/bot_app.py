import asyncio
import logging

import aiogram
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from dependencies.redis_service_dep import redis_client
from drug_search.bot.handlers.start_handler import router as router0
from drug_search.bot.handlers.drug_database_handler import router as router1
from drug_search.bot.handlers.profile_handler import router as router2
from drug_search.bot.middlewares.depends_injectors import DependencyInjectionMiddleware
from drug_search.config import config


def setup_auth(dp: Dispatcher):
    # Регистрация middleware
    dp.update.outer_middleware(DependencyInjectionMiddleware())

    # Регистрация хендлеров (порядок важен)
    for router in [
        router2,
        router1,
        router0,
    ]:
        dp.include_router(router)


async def start_polling(dp: Dispatcher):
    await dp.start_polling(bot)


storage = RedisStorage(redis_client)
dp = Dispatcher(storage=storage)

bot = aiogram.Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)


def logging_cfg():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


if __name__ == "__main__":
    logging_cfg()

    setup_auth(dp)
    asyncio.run(start_polling(dp))
