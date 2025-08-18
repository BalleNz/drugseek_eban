from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject


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

        # 3. Проверяем токен
        user_data = await state.get_data()
        if not user_data.get("access_token"):
            return await event.answer("Требуется авторизация! Нажмите /login")

        # 4. Продолжаем цепочку обработки
        return await handler(event, data)
