import uuid
from uuid import UUID

from drug_search.bot.api_client.base_http_client import BaseHttpClient, HTTPMethod
from drug_search.core.lexicon import DANGER_CLASSIFICATION
from drug_search.core.schemas import (UserTelegramDataSchema, UserSchema, DrugExistingResponse,
                                      DrugSchema, QuestionAssistantResponse, AllowedDrugsSchema,
                                      SelectActionResponse, QuestionRequest, AddTokensRequest,
                                      BuyDrugRequest, BuyDrugResponse, UpdateDrugResponse, QuestionContinueRequest)


class DrugSearchAPIClient(BaseHttpClient):
    """Универсальный клиент для DrugSearch API"""

    # [ Assistant handler ]
    async def assistant_get_action(self, access_token: str, query: str) -> SelectActionResponse:
        return await self._request(
            HTTPMethod.POST,
            endpoint="/v1/assistant/actions/predict_action",
            request_body={"query": query},
            access_token=access_token,
            response_model=SelectActionResponse
        )

    async def question_answer(
            self,
            access_token: str,
            user_telegram_id: str,
            question: str,
            message_id: str
    ) -> QuestionAssistantResponse:
        return await self._request(
            HTTPMethod.POST,
            endpoint="/v1/assistant/actions/question",
            request_body=QuestionRequest(
                user_telegram_id=user_telegram_id,
                question=question,
                old_message_id=message_id,
            ),
            access_token=access_token,
        )

    async def question_answer_continue(
            self,
            access_token: str,
            user_telegram_id: str,
            question: str,
            message_id: str,
    ) -> QuestionAssistantResponse:
        return await self._request(
            HTTPMethod.POST,
            endpoint="/v1/assistant/actions/question_continue",
            request_body=QuestionContinueRequest(
                user_telegram_id=user_telegram_id,
                question=question,
                old_message_id=message_id,
            ),
            access_token=access_token
        )

    # [ Auth handler ]
    async def telegram_auth(self, telegram_user_data: UserTelegramDataSchema) -> str:
        response: dict = await self._request(
            HTTPMethod.POST,
            "/v1/auth/",
            request_body=telegram_user_data.model_dump()
        )
        return response["token"]

    # [ User handler ]
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
            amount_search_tokens: int = 0,
            amount_question_tokens: int = 0
    ) -> None:
        """Добавление токенов"""
        await self._request(
            HTTPMethod.POST,
            "/v1/user/tokens/increment",
            access_token=access_token,
            request_body=AddTokensRequest(
                amount_search_tokens=amount_search_tokens,
                amount_question_tokens=amount_question_tokens,
            )
        )

    async def reduce_tokens(
            self,
            access_token: str,
            amount_search_tokens: int = 0,
            amount_question_tokens: int = 0
    ):
        """Отнимает токены"""
        await self._request(
            HTTPMethod.POST,
            endpoint="/v1/user/tokens/reduce",
            access_token=access_token,
            request_body=AddTokensRequest(
                amount_search_tokens=amount_search_tokens,
                amount_question_tokens=amount_question_tokens,
            )
        )

    # [ Drug handler ]
    async def update_drug(
            self,
            drug_id: uuid.UUID,
            access_token: str
    ):
        return await self._request(
            endpoint=f"/v1/drugs/update/{drug_id}",
            method=HTTPMethod.POST,
            access_token=access_token,
            response_model=UpdateDrugResponse,
        )

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

    async def search_drug_without_trigrams(
            self,
            drug_name_query: str,
            access_token: str
    ):
        """Поиск препарата без триграмм"""
        return await self._request(
            HTTPMethod.GET,
            endpoint=f"/v1/drugs/search/without_trigrams/{drug_name_query}",
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

    async def buy_drug(
            self,
            drug_name: str,
            drug_id: uuid.UUID | None,  # exist in database
            danger_classification: DANGER_CLASSIFICATION,
            access_token: str
    ) -> BuyDrugResponse:
        """Разрешение препарата.
        Если не существует в БД —> создает.
        """
        return await self._request(
            HTTPMethod.POST,
            f"/v1/user/buy_drug",
            access_token=access_token,
            request_body=BuyDrugRequest(
                drug_name=drug_name,
                drug_id=drug_id,
                danger_classification=danger_classification
            ),
            response_model=BuyDrugResponse
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
