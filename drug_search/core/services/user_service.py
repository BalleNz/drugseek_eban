import uuid
from uuid import UUID

from drug_search.core.schemas import AllowedDrugsSchema, UserSchema
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
        # TODO в Arq
        user: UserSchema = await self.repo.get(user_id)
        user_drugs = await self.repo.get_allowed_drug_names(user_id=user.id)

        user_description: str = await self.assistant.get_user_description(
            user_name=user.first_name + user.last_name,
            user_drug_names=user_drugs
        )
        await self.repo.update_user_description(description=user_description, user_id=user.id)

    async def add_tokens(
            self,
            user_id: uuid.UUID,
            amount_search_tokens: int = 1,
            amount_question_tokens: int = 0
    ) -> None:
        """Добавляет запросы юзеру"""
        await self.repo.increment_user_requests(
            user_id=user_id,
            amount_search_tokens=amount_search_tokens,
            amount_question_tokens=amount_question_tokens
        )

    async def reduce_tokens(
            self,
            user_id: uuid.UUID,
            amount_search_tokens: int = 1,
            amount_question_tokens: int = 0
    ) -> None:
        """Отнимает запросы у юзера"""
        await self.add_tokens(user_id, -amount_search_tokens, -amount_question_tokens)

    async def add_request_log(self, user_id: uuid.UUID, query: str):
        ...

    async def get_allowed_drugs_info(self, user_id: uuid.UUID) -> AllowedDrugsSchema:
        """Возвращает количество препаратов в базе, количество разрешенных и краткую информацию о каждом разрешенном."""
        return await self.repo.get_allowed_drugs_info(user_id=user_id)
