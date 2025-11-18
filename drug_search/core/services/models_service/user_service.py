import uuid
from uuid import UUID

from drug_search.core.schemas import UserSchema, AllowedDrugsInfoSchema, AssistantResponseUserDescription
from drug_search.core.services.assistant_service import AssistantService
from drug_search.infrastructure.database.repository.user_repo import UserRepository


class UserService:
    def __init__(
            self,
            repo: UserRepository,
            assistant_service: AssistantService = None,
    ):
        self.repo = repo
        self.assistant = assistant_service

    async def allow_drug_to_user(self, user_id: UUID, drug_id: UUID) -> None:
        """Разрешает препарат юзеру."""
        return await self.repo.allow_drug_to_user(user_id=user_id, drug_id=drug_id)

    async def update_user_description(self, user_id: UUID) -> None:
        """Обновляет информацию описания юзера."""
        user: UserSchema = await self.repo.get(user_id)
        user_drugs = await self.repo.get_allowed_drugs_info(user_id=user.id)
        user_drugs_name: str = ', '.join(drug.drug_name_ru for drug in user_drugs.allowed_drugs)

        if user.last_name:
            user_name: str = user.first_name + user.last_name
        else:
            user_name: str = user.first_name if user.first_name else user.username

        user_description: AssistantResponseUserDescription = await self.assistant.get_user_description(
            user_name=user_name,
            user_drugs_name=user_drugs_name
        )
        await self.repo.update_user_description(description=user_description.user_description, user_id=user.id)

    async def add_tokens(
            self,
            user_id: uuid.UUID,
            amount_search_tokens: int = 0,
    ) -> None:
        """Добавляет запросы юзеру"""
        await self.repo.increment_user_requests(
            user_id=user_id,
            tokens_amount=amount_search_tokens,
        )

    async def reduce_tokens(
            self,
            user_id: uuid.UUID,
            tokens_amount: int = 0,
    ) -> None:
        """Отнимает запросы у юзера"""
        await self.add_tokens(user_id, -tokens_amount)

    async def add_request_log(self, user_id: uuid.UUID, query: str):
        ...

    async def get_allowed_drugs_info(self, user_id: uuid.UUID) -> AllowedDrugsInfoSchema:
        """Возвращает количество препаратов в базе, количество разрешенных и краткую информацию о каждом разрешенном."""
        return await self.repo.get_allowed_drugs_info(user_id=user_id)
