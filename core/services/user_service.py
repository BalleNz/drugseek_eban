from uuid import UUID

from fastapi import Depends

from assistant import assistant
from database.repository.user_repo import UserRepository, get_user_repository
from schemas.user import UserTelegramDataSchema, UserSchema


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def allow_drug_to_user(self, user_id: UUID, drug_id: UUID) -> None:
        return await self.repo.allow_drug_to_user(user_id=user_id, drug_id=drug_id)

    async def update_user_description(self, user_id: UUID):
        user: UserSchema = await self.repo.get(user_id)
        user_drugs = await self.repo.get_allowed_drug_names(user_id=user.id)

        user_description = assistant.get_user_description(
            user_name=user.first_name + user.last_name,
            user_drug_names=user_drugs
        )
        await self.repo.update_user_description(description=user_description, user_id=user.id)


def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo=repo)
