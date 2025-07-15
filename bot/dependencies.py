from punq import Container
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.engine import get_async_session
from core.database.repository.drug import DrugRepository
from core.services.drug import DrugService

container = Container()

# FUTURE: МБ УБРАТЬ?


def register_dependencies():
    """
    Регистрация всех зависимостей для DI.
    Используется готовое решение: punq.
    """
    # TODO: сделать цикл, брать модели из модуля __init__
    container.register(AsyncSession, factory=get_async_session, scope="request")
    container.register(DrugRepository)

    container.register(DrugService)
