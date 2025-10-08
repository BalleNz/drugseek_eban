from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from api_client.drug_search_api import DrugSearchAPIClient
from dependencies.api_client_dep import get_api_client
from drug_search.core.dependencies.cache_service_dep import get_cache_service
from drug_search.core.services.cache_service import CacheService


class DependencyInjectionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Инициализируем клиенты
        cache_service: CacheService = await get_cache_service()

        # Добавляем в контекст
        data['cache_service'] = cache_service

        api_client: DrugSearchAPIClient = get_api_client()
        data["api_client"] = api_client

        try:
            # Получаем access token и сохраняем к контекст
            user: User = data.get('event_from_user')
            if user:
                from drug_search.core.schemas import UserTelegramDataSchema

                telegram_data = UserTelegramDataSchema(
                    telegram_id=str(user.id),
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name
                )

                access_token = await cache_service.get_or_refresh_access_token(telegram_data)
                data['access_token'] = access_token

            result = await handler(event, data)

        finally:
            # Очистка ресурсов
            await cache_service.api_client.close()
            await cache_service.redis_service.redis.close()

        return result
