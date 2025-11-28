import logging
import time
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware, Bot
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject, User, InlineKeyboardMarkup

from drug_search.bot.keyboards.keyboard_markups import get_subscription_packages_keyboard, \
    get_subscription_packages_types_keyboard
from drug_search.bot.lexicon.message_text import MessageText
from drug_search.bot.utils.funcs import get_telegram_schema_from_data, format_time, format_rate_limit, what_subscription
from drug_search.core.dependencies.bot.cache_service_dep import get_cache_service
from drug_search.core.dependencies.redis_service_dep import get_redis_service
from drug_search.core.lexicon import SUBSCRIPTION_TYPES, ANTISPAM_DEFAULT, ANTISPAM_LITE
from drug_search.core.schemas import UserSchema, UserTelegramDataSchema
from drug_search.core.services.cache_logic.cache_service import CacheService
from drug_search.core.services.cache_logic.redis_service import RedisService

logger = logging.getLogger(__name__)


class MessageLimitsMiddleware(BaseMiddleware):
    def __init__(self):
        self.redis_service: RedisService = get_redis_service()
        self.limits = {
            SUBSCRIPTION_TYPES.DEFAULT: ANTISPAM_DEFAULT,
            SUBSCRIPTION_TYPES.LITE: ANTISPAM_LITE,
        }

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any]
    ) -> Any:
        # [ is antispam flag ]
        is_antispam_flag: bool = get_flag(data, "antispam")
        if not is_antispam_flag:
            return await handler(event, data)

        # [ deps ]
        cache_service: CacheService = await get_cache_service()

        # [ variables ]
        bot: Bot = data.get("bot")
        telegram_user_data: User = data.get('event_from_user')
        telegram_data: UserTelegramDataSchema = await get_telegram_schema_from_data(telegram_user_data)
        chat_id: str = telegram_data.telegram_id

        access_token: str = await cache_service.get_or_refresh_access_token(telegram_data)
        user: UserSchema = await cache_service.get_user_profile(access_token, telegram_data.telegram_id)

        # [ skip if Premium ]
        if user.subscription_type == SUBSCRIPTION_TYPES.PREMIUM:
            return await handler(event, data)

        user_limits = self.limits[user.subscription_type]
        max_requests, time_limit = user_limits['max_requests'], user_limits['time_limit']

        redis_key: str = f"antispam_limits:{user.telegram_id}"

        now = time.time()

        async with self.redis_service.redis.pipeline(transaction=True) as pipe:
            await pipe.hgetall(redis_key)  # получение всех полей в хеше redis_key
            current_data = await pipe.execute()
            current = current_data[0] if current_data else {}

            # [ первое сообщение ]
            if not current:
                await pipe.hset(redis_key, mapping={
                    "max_requests": str(max_requests - 1),
                    "last_update": str(now)
                })
                await pipe.expire(redis_key, time_limit)
                await pipe.execute()
                return await handler(event, data)

            # [ прошло ли время лимита ]
            last_update = float(current.get("last_update"))
            if now - last_update >= time_limit:
                await pipe.hset(redis_key, mapping={
                    "max_requests": str(max_requests - 1),
                    "last_update": str(now)
                })
                await pipe.expire(redis_key, time_limit)
                await pipe.execute()
                return await handler(event, data)

            message_count_now = float(current["max_requests"])

            # [ сообщение выслано ]
            if message_count_now >= 1:
                message_count_now -= 1
                await pipe.hset(redis_key, mapping={
                    "max_requests": str(message_count_now),
                    "last_update": current["last_update"]
                })
                await pipe.expire(redis_key, time_limit)
                await pipe.execute()
            # [ лимит закончился ]
            else:
                remaining_time: int = await self.get_remaining_time(redis_key)
                await self.send_limit_message(bot, chat_id, user.subscription_type, remaining_time)
                return

            return await handler(event, data)

    async def get_remaining_time(self, key: str) -> int:
        """Получить оставшееся время до сброса лимита"""
        ttl = await self.redis_service.redis.ttl(key)
        return ttl

    async def send_limit_message(
            self,
            bot: Bot,
            chat_id: str,
            user_subscription: SUBSCRIPTION_TYPES,
            remaining_time: int,
    ):
        """Отправляем информационное сообщение о лимите"""
        max_requests, time_window = self.limits[user_subscription].values()

        message = MessageText.ANTISPAM_MESSAGE.format(
            time_left=format_time(remaining_time),
            what_subscription=what_subscription(user_subscription),
            message_rate=format_rate_limit(message_count=max_requests, interval_seconds=time_window)
        )

        keyboard: InlineKeyboardMarkup = get_subscription_packages_types_keyboard(user_subscription_type=user_subscription)

        await bot.send_message(chat_id=chat_id, text=message, reply_markup=keyboard)
