from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from drug_search.bot.api_client.drug_search_api import get_api_client
from services.redis_service import get_redis_client

handlers_that_use_api_client = [
    None
]

handlers_that_use_redis = [
    "drug_menu_handler",
    "drug_list_handler",
    "drug_describe_handler"
]


class DependencyInjectionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Инициализируем клиенты
        api_client = await get_api_client()
        redis_service = await get_redis_client()

        # Добавляем в контекст
        data['api_client'] = api_client
        data['redis_service'] = redis_service

        try:
            # Получаем access token и сохраняем к контекст
            user: User = data.get('event_from_user')
            if user:
                from drug_search.core.schemas import UserTelegramDataSchema

                telegram_data = UserTelegramDataSchema(
                    telegram_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name
                )

                access_token = await redis_service.get_or_refresh_access_token(telegram_data)
                data['access_token'] = access_token

            result = await handler(event, data)

        finally:
            # Очистка ресурсов
            await api_client.close()
            await redis_service.redis.close()

        return result
