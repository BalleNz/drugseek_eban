import inspect

from aiogram import BaseMiddleware

from core.dependencies import container


class DIMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # 1. Анализируем параметры обработчика
        sig = inspect.signature(handler)

        # 2. Проверяем каждый параметр
        for name, param in sig.parameters.items():
            # 3. Если тип параметра зарегистрирован в контейнере
            if param.annotation in container:
                # 4. Создаем объект и добавляем в data
                data[name] = container.resolve(param.annotation)

        return await handler(event, data)
