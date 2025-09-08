# middleware.py
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient, get_api_client
from services.redis_service import RedisService, get_redis_client

handlers_that_use_api_client = [
    None
]

handlers_that_use_redis = [
    "drug_menu_handler",
    "drug_list_handler",
    "drug_describe_handler"
]


class APIClientMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # skip if not in "handlers_that_uses_api_client"
        if event.text not in handlers_that_use_api_client:
            return await handler(event, data)

        # Создаем клиент и добавляем в данные
        client: DrugSearchAPIClient = await get_api_client()
        data['api_client'] = client

        try:
            result = await handler(event, data)
        finally:
            # Закрываем клиент после работы хендлера и вроде как сборщик мусора заберет всю хуйню
            await client.close()

        return result


class RedisServiceMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        if event.text not in handlers_that_use_redis:
            return await handler(event, data)

        # Создаем клиент и добавляем в данные
        redis_service: RedisService = await get_redis_client()
        data['redis_service'] = redis_service

        try:
            result = await handler(event, data)
        finally:
            await redis_service.redis.close()
            await redis_service.api_client.close()

        return result
