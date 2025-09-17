from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import get_async_session
from drug_search.core.dependencies.assistant_service_dep import get_assistant_service
from drug_search.core.services.assistant_service import AssistantService
from drug_search.core.services.user_service import UserService
from drug_search.infrastructure.database.repository.user_repo import UserRepository


async def get_user_repository(
        session_generator: AsyncGenerator[AsyncSession, None] = Depends(get_async_session)
) -> UserRepository:
    """
    :return: UserRepository obj with AsyncSession for onion service layer
    """
    async with session_generator as session:
        return UserRepository(session=session)


async def get_user_service(
        repo: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(repo=repo)


async def get_user_service_with_assistant(
        repo: UserRepository = Depends(get_user_repository),
        assistant_service: AssistantService = Depends(get_assistant_service)
) -> UserService:
    """Для зависимостей, которые используют ассистента"""
    return UserService(repo=repo, assistant_service=assistant_service)
