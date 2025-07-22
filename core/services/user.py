from uuid import UUID

from fastapi import Depends

from database.models.user import User
from database.repository.user import UserRepository, get_user_repository
from schemas.drug_schemas import DrugSchema
from schemas.user import UserTelegramDataSchema, UserSchema


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_or_create_from_telegram(self, telegram_user: UserTelegramDataSchema) -> UserSchema:
        user_model = await self.repo.get_by_telegram_id(telegram_user.id)

        if not user_model:
            user_model = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
            )
            user_model = await self.repo.create(user_model)
        user: UserSchema = UserSchema.model_validate(user_model)
        return user

    async def allow_drug_to_user(self, user: User, drug_id: UUID) -> User:
        return await user.add_allowed_drug_by_id(drug_id=drug_id, session=self.repo._session)

    async def update_user_description(self, user: User):
        pass


def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo=repo)
