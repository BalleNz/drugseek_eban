import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user import User
from database.repository.base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=User, session=session)

    async def allow_drug_to_user(self, drug_id: uuid.UUID, user_id: uuid.UUID):
        pass
