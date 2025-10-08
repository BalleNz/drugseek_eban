from uuid import UUID

from drug_search.bot.api_client.base_http_client import BaseHttpClient, HTTPMethod
from drug_search.core.schemas import (UserTelegramDataSchema, UserSchema, DrugExistingResponse,
                                      DrugSchema, QuestionAssistantResponse, AllowedDrugsSchema,
                                      SelectActionResponse, QuestionRequest, AddTokensRequest)


class DrugSearchAPIClient(BaseHttpClient):
    """Универсальный клиент для DrugSearch API"""

    # assistant handler
    async def assistant_get_action(self, access_token: str, query: str) -> SelectActionResponse:
        return await self._request(
            HTTPMethod.POST,
            endpoint="/v1/assistant/actions/predict_action",
            request_body={"query": query},
            access_token=access_token,
            response_model=SelectActionResponse
        )

    async def action_answer(
            self,
            access_token: str,
            user_telegram_id: str,
            question: str,
            old_message_id: str
    ) -> QuestionAssistantResponse:
        return await self._request(
            HTTPMethod.POST,
            endpoint="/v1/assistant/actions/question",
            request_body=QuestionRequest(
                user_telegram_id=user_telegram_id,
                question=question,
                old_message_id=old_message_id,
            ),
            access_token=access_token,
        )

    # Auth endpoints
    async def telegram_auth(self, telegram_user_data: UserTelegramDataSchema) -> str:
        response: dict = await self._request(
            HTTPMethod.POST,
            "/v1/auth/",
            request_body=telegram_user_data.model_dump()
        )
        return response["token"]

    # User endpoints
    async def get_current_user(self, access_token: str) -> UserSchema:
        """Получение текущего пользователя"""
        return await self._request(
            HTTPMethod.GET,
            "/v1/user/",
            response_model=UserSchema,
            access_token=access_token
        )

    async def get_allowed_drugs(self, access_token: str) -> AllowedDrugsSchema:
        """Получение разрешенных препаратов"""
        return await self._request(
            HTTPMethod.GET,
            "/v1/user/allowed",
            response_model=AllowedDrugsSchema,
            access_token=access_token
        )

    async def add_tokens(
            self,
            access_token: str,
            amount_search_tokens: int = 1,
            amount_question_tokens: int = 0
    ) -> None:
        """Добавление токенов"""
        await self._request(
            HTTPMethod.POST,
            "/v1/user/tokens",
            access_token=access_token,
            request_body=AddTokensRequest(
                amount_search_tokens=amount_search_tokens,
                amount_question_tokens=amount_question_tokens,
            )
        )

    # Drug endpoints
    async def search_drug(
            self,
            user_query: str,
            access_token: str
    ) -> DrugExistingResponse:
        """Поиск препарата"""
        return await self._request(
            HTTPMethod.GET,
            f"/v1/drugs/search/{user_query}",
            response_model=DrugExistingResponse,
            access_token=access_token
        )

    async def search_drug_trigrams(
            self,
            drug_name_query: str,
            access_token: str
    ) -> DrugExistingResponse:
        """Поиск препарата триграммами"""
        return await self._request(
            HTTPMethod.GET,
            endpoint=f"/v1/drugs/search/trigrams/{drug_name_query}",
            response_model=DrugExistingResponse,
            access_token=access_token
        )

    async def get_drug(
            self,
            drug_id: UUID,
            access_token: str
    ) -> DrugSchema:
        """Получить препарат по его ID"""
        return await self._request(
            HTTPMethod.GET,
            endpoint=f"/v1/drugs/{drug_id}",
            response_model=DrugSchema,
            access_token=access_token
        )

    async def allow_drug(
            self,
            drug_id: UUID,
            access_token: str
    ) -> dict:
        """Разрешение препарата"""
        return await self._request(
            HTTPMethod.POST,
            f"/v1/drugs/allow/{drug_id}",
            access_token=access_token
        )

    async def update_drug_researches(
            self,
            drug_id: UUID,
            access_token: str
    ) -> DrugSchema:
        """Обновление исследований препарата"""
        return await self._request(
            HTTPMethod.POST,
            f"/v1/drugs/update/{drug_id}/researches",
            response_model=DrugSchema,
            access_token=access_token
        )
