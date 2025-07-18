from uuid import UUID

from fastapi import Depends

from database.models.user import User
from database.repository.user import UserRepository, get_user_repository


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def allow_drug_to_user(self, user: User, drug_id: UUID) -> User:
        return await user.add_allowed_drug_by_id(drug_id=drug_id, session=self.repo._session)

    async def update_user_description(self, user: User):
        pass


def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo=repo)
