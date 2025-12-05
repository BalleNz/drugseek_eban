import asyncio
import json
from uuid import UUID

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from drug_search.bot.bot_instance import bot
from drug_search.bot.handlers.actions import router as drug_actions_router
from drug_search.bot.handlers.admin_tools import router as admin_router
from drug_search.bot.handlers.database import router as database_router
from drug_search.bot.handlers.help import router as help_router
from drug_search.bot.handlers.main import router as main_router
from drug_search.bot.handlers.profile import router as profile_router
from drug_search.bot.handlers.referrals import router as referrals_router
from drug_search.bot.handlers.start import router as start_router
from drug_search.bot.handlers.yookassa import router as yookassa_router
from drug_search.bot.middlewares.depends_injectors import DependencyInjectionMiddleware
from drug_search.bot.middlewares.limits import MessageLimitsMiddleware
from drug_search.core.dependencies.redis_service_dep import redis_client
from drug_search.infrastructure.loggerConfig import configure_logging


def setup_auth(dp: Dispatcher):
    # Регистрация middleware
    dp.update.outer_middleware(DependencyInjectionMiddleware())
    dp.message.middleware(MessageLimitsMiddleware())

    # Регистрация хендлеров (порядок важен)
    for router in [
        start_router,
        help_router,
        yookassa_router,
        admin_router,
        database_router,
        profile_router,
        referrals_router,
        main_router,
        drug_actions_router,
    ]:
        dp.include_router(router)


async def start_polling(dp: Dispatcher):
    await dp.start_polling(bot)


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


storage = RedisStorage(
    redis_client,
    state_ttl=60*60*6,  # 6 часов
    json_dumps=lambda obj: json.dumps(obj, cls=UUIDEncoder),
    json_loads=json.loads
)
dp = Dispatcher(storage=storage)

if __name__ == "__main__":
    setup_auth(dp)
    configure_logging()
    asyncio.run(start_polling(dp))
