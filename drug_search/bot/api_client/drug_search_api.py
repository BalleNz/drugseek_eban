from uuid import UUID

from drug_search.bot.api_client.base_http_client import BaseHttpClient, HTTPMethod
from drug_search.core.schemas import UserTelegramDataSchema, UserSchema, DrugExistingResponse, DrugSchema
from drug_search.core.schemas.telegram_schemas import AllowedDrugsSchema


class DrugSearchAPIClient(BaseHttpClient):
    """Универсальный клиент для DrugSearch API"""

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

    async def add_tokens(self, access_token: str, tokens_amount: int) -> None:
        """Добавление токенов"""
        await self._request(
            HTTPMethod.PUT,
            "/v1/user/tokens",
            access_token=access_token,
            request_body={"tokens_amount": tokens_amount}
        )

    # Drug endpoints
    async def search_drug(
            self,
            user_query: str,
            access_token: str
    ) -> DrugExistingResponse:
        """Поиск препарата"""
        return await self._request(
            HTTPMethod.POST,
            f"/v1/drugs/search/{user_query}",
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
            f"/v1/drugs/update/researchs/{drug_id}",
            response_model=DrugSchema,
            access_token=access_token
        )
