from uuid import UUID

from fastapi import Depends

from database.repository.user import UserRepository, get_user_repository
from schemas.user import UserTelegramDataSchema, UserSchema


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def allow_drug_to_user(self, user_id: UUID, drug_id: UUID) -> None:
        return await self.repo.allow_drug_to_user(user_id=user_id, drug_id=drug_id)

    async def update_user_description(self, user_id: UUID):
        pass


def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo=repo)
