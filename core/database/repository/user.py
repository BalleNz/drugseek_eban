import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import get_async_session
from database.models.user import User
from database.repository.base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=User, session=session)

    async def allow_drug_to_user(self, drug_id: uuid.UUID, user_id: uuid.UUID):
        pass


def get_user_repository(session: AsyncSession = Depends(get_async_session)) -> UserRepository:
    """
    :return: UserRepository obj with AsyncSession for onion service layer
    """
    return UserRepository(session=session)
