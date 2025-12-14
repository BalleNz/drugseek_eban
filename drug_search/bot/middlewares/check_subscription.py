import logging
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware, Bot
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject, User, InlineKeyboardMarkup

from drug_search.bot.keyboards.keyboard_markups import get_subscription_packages_types_keyboard
from drug_search.bot.lexicon.message_text import MessageText
from drug_search.bot.utils.funcs import get_telegram_schema_from_data
from drug_search.core.dependencies.bot.cache_service_dep import get_cache_service
from drug_search.core.dependencies.redis_service_dep import get_redis_service
from drug_search.core.lexicon import SUBSCRIPTION_TYPES, ZMTLK_CHANNEL_URL
from drug_search.core.schemas import UserSchema, UserTelegramDataSchema
from drug_search.core.services.cache_logic.cache_service import CacheService
from drug_search.core.services.cache_logic.redis_service import RedisService
from drug_search.core.utils.subscription_check import is_user_subscribed

logger = logging.getLogger(__name__)


class CheckSubscriptionMiddleware(BaseMiddleware):
    """
    Проверяет обязательную подписку на канал для людей без подписки
    """

    def __init__(self):
        self.redis_service: RedisService = get_redis_service()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any]
    ) -> Any:
        # [ is check_subscription flag ]
        is_check_subscription_flag: bool = get_flag(data, "check_subscription")
        if not is_check_subscription_flag:
            return await handler(event, data)

        # [ deps ]
        cache_service: CacheService = await get_cache_service()
        channel_username: str = ZMTLK_CHANNEL_URL

        # [ variables ]
        bot: Bot = data.get("bot")
        telegram_user_data: User = data.get('event_from_user')
        telegram_data: UserTelegramDataSchema = await get_telegram_schema_from_data(telegram_user_data)
        chat_id: str = telegram_data.telegram_id

        access_token: str = await cache_service.get_or_refresh_access_token(telegram_data)
        user: UserSchema = await cache_service.get_user_profile(access_token, telegram_data.telegram_id)

        # [ skip if user_subscription ]
        if user.subscription_type in [SUBSCRIPTION_TYPES.LITE, SUBSCRIPTION_TYPES.PREMIUM]:
            return await handler(event, data)

        redis_key: str = f"check_subscription:{user.telegram_id}"

        is_subscribed: bool | None = await cache_service.redis_service.redis.get(redis_key)
        if not is_subscribed:
            is_subscribed: bool = await is_user_subscribed(
                user.telegram_id,
                channel_username,
                bot
            )

            if not is_subscribed:
                await self.send_limit_message(
                    bot,
                    chat_id,
                    user.subscription_type
                )
            else:
                await cache_service.redis_service.redis.set(redis_key, 1, ex=1800)

    async def send_limit_message(
            self,
            bot: Bot,
            chat_id: str,
            user_subscription: SUBSCRIPTION_TYPES,
    ):
        """Отправляем информационное сообщение о лимите"""
        message = MessageText.MESSAGE_NEED_SUBSCRIPTION

        keyboard: InlineKeyboardMarkup = get_subscription_packages_types_keyboard(
            user_subscription_type=user_subscription)

        await bot.send_message(chat_id=chat_id, text=message, reply_markup=keyboard)
