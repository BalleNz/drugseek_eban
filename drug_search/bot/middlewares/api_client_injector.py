# middleware.py
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient, get_api_client


handlers_that_uses_api_client = [
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
        if event.text not in handlers_that_uses_api_client:
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