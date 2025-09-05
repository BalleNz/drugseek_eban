import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # 1. Пропускаем команды, не требующие авторизации
        if event.text in ['/start', '/help', '/login']:
            return await handler(event, data)

        # 2. Получаем состояние пользователя
        state: FSMContext = data.get("state")
        if not state:
            return await event.answer("Системная ошибка. Попробуйте позже.")

        # 3. обработка токена
        user_data = await state.get_data()
        access_token = user_data.get("access_token")

        if ...:
            api_client: ... = ...
            try:
                response = await api_client.login_via_telegram(  # TODO
                    telegram_id=...,
                    first_name=...,
                    last_name=...,
                    username=...
                )

                # 4. Сохраняем токен в FSM
                # TODO

                logger.info("✅ Вы успешно авторизованы!")
            except:
                ...

        return await handler(event, data)
