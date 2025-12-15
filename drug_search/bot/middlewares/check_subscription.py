import logging
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware, Bot
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject, User, InlineKeyboardMarkup

from keyboards.other_keyboards import check_subscription_condition
from drug_search.bot.lexicon.message_text import MessageText
from drug_search.bot.utils.funcs import get_telegram_schema_from_data
from drug_search.core.dependencies.bot.cache_service_dep import get_cache_service
from drug_search.core.dependencies.redis_service_dep import get_redis_service
from drug_search.core.lexicon import SUBSCRIPTION_TYPES, ZMTLK_CHANNEL_USERNAME
from drug_search.core.schemas import UserSchema, UserTelegramDataSchema
from drug_search.core.services.cache_logic.cache_service import CacheService
from drug_search.core.services.cache_logic.redis_service import RedisService
from drug_search.core.utils.subscription_check import check_subscription_with_retry

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
        channel_username: str = ZMTLK_CHANNEL_USERNAME

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
            message = MessageText.MESSAGE_NEED_SUBSCRIPTION

            await self.send_message(
                bot,
                chat_id,
                message,
                True
            )

            is_subscribed: bool = await check_subscription_with_retry(
                user.telegram_id,
                channel_username,
                bot
            )

            if is_subscribed:
                message = "Теперь ты можешь пользоваться ботом!"
                await self.send_message(
                    bot,
                    chat_id,
                    message,
                    False
                )
                await cache_service.redis_service.redis.set(redis_key, 1, ex=1800)
        else:
            return await handler(event, data)

    async def send_message(
            self,
            bot: Bot,
            chat_id: str,
            message: str,
            need_keyboard: bool
    ):
        """Отправляем информационное сообщение о лимите"""

        keyboard: InlineKeyboardMarkup | None
        if need_keyboard:
            keyboard = check_subscription_condition()
        else:
            keyboard = None

        await bot.send_message(chat_id=chat_id, text=message, reply_markup=keyboard)
