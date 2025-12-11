import logging
from typing import Union, Type

import aiohttp
from openai import AsyncOpenAI, NOT_GIVEN, NotGiven
from pydantic import ValidationError

from drug_search.config import config
from drug_search.core.lexicon import Prompts
from drug_search.core.schemas import (
    DrugResearchesAssistantResponse, AssistantResponsePubmedQuery,
    DrugBrieflyAssistantResponse, DrugCombinationsAssistantResponse,
    DrugPathwaysAssistantResponse, AssistantResponseDrugValidation,
    SelectActionResponse, QuestionDrugsAssistantResponse,
    AssistantResponseUserDescription, DrugDosagesAssistantResponse, DrugAnalogsAssistantResponse,
    DrugMetabolismAssistantResponse, ClearResearchesRequest, QuestionAssistantResponse
)
from drug_search.core.utils import assistant_utils
from drug_search.core.utils.exceptions import AssistantResponseError, APIError

logger = logging.getLogger(__name__)

AssistantResponseModel = Union[
    DrugPathwaysAssistantResponse,
    DrugBrieflyAssistantResponse,
    DrugCombinationsAssistantResponse,
    AssistantResponseDrugValidation,
    DrugResearchesAssistantResponse,
    None,
]


class AssistantService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        self.actions = self.Actions(self)
        self.drug_creation = self.DrugCreation(self)
        self.pubmed = self.PubMed(self)
        self._session: aiohttp.ClientSession | None = None

    async def check_balance(self):
        """Асинхронная проверка баланса"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        "https://api.deepseek.com/user/balance",
                        headers={
                            'Accept': 'application/json',
                            'Authorization': f'Bearer {config.DEEPSEEK_API_KEY}'
                        }
                ) as response:
                    balance_data = await response.json()

                    usd_balance_info = next(
                        (item for item in balance_data["balance_infos"] if item["currency"] == "USD"),
                        None
                    )
                    balance_now: float = float(usd_balance_info["total_balance"]) if usd_balance_info else 0.0

                    if balance_now > config.MINIMUM_USD_ON_BALANCE:
                        logger.info(f"Выполняется запрос, на балансе: {balance_now}")
                        return

                    logger.error(f"На балансе недостаточно денег: {balance_now} < {config.MINIMUM_USD_ON_BALANCE}")
                    raise APIError("На балансе DeepseekAPI недостаточно денег!")

        except aiohttp.ClientError as e:
            logger.error(f"Ошибка при проверке баланса: {e}")
            return

    async def get_response(
            self,
            input_query: str,
            prompt: str,
            pydantic_model: Type[AssistantResponseModel],
            temperature: float = 0.3,
            max_completion_tokens: int | NotGiven = NOT_GIVEN
    ):
        try:
            await self.check_balance()

            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": f"{prompt}"},
                    {"role": "user", "content": f"{input_query}"}
                ],
                response_format={"type": "json_object"},
                temperature=temperature,
                max_completion_tokens=max_completion_tokens
            )

            if not response.choices:
                raise AssistantResponseError("ERROR: No data from assistant.")

            try:
                if pydantic_model:
                    return pydantic_model.model_validate_json(response.choices[0].message.content)

                # если нет Pydantic модели —> возвращает строку.
                return response.choices[0].message.content
            except ValidationError as e:
                logger.error(f"Validation error: {e}")
                logger.error(f"Input Query: {input_query}")
                logger.error(f"Raw response: {response.choices[0].message.content}\n\n"
                             f"Model: {pydantic_model}")
                raise ValueError(f"Invalid assistant response: {e}")

        except Exception as ex:
            logger.error(f"Error in get_response: {ex}")
            raise

    class DrugCreation:
        def __init__(self, assistant_service):
            self.assistant_service = assistant_service

        async def get_drug_briefly_info(self, drug_name: str) -> DrugBrieflyAssistantResponse:
            return await self.assistant_service.get_response(
                input_query=drug_name,
                prompt=Prompts.GET_DRUG_BRIEFLY_INFO,
                pydantic_model=DrugBrieflyAssistantResponse
            )

        async def get_drug_dosages(self, drug_name: str) -> DrugDosagesAssistantResponse:
            return await self.assistant_service.get_response(
                input_query=drug_name,
                prompt=Prompts.GET_DRUG_DOSAGES,
                pydantic_model=DrugDosagesAssistantResponse
            )

        async def get_analogs(self, drug_name: str) -> DrugAnalogsAssistantResponse:
            return await self.assistant_service.get_response(
                input_query=drug_name,
                prompt=Prompts.GET_DRUG_ANALOGS,
                pydantic_model=DrugAnalogsAssistantResponse
            )

        async def get_metabolism(self, drug_name: str) -> DrugMetabolismAssistantResponse:
            return await self.assistant_service.get_response(
                input_query=drug_name,
                prompt=Prompts.GET_DRUG_METABOLISM,
                pydantic_model=DrugMetabolismAssistantResponse
            )

        async def get_pathways(self, drug_name: str) -> DrugPathwaysAssistantResponse:
            return await self.assistant_service.get_response(
                input_query=drug_name,
                prompt=Prompts.GET_DRUG_PATHWAYS,
                pydantic_model=DrugPathwaysAssistantResponse
            )

        async def get_combinations(self, drug_name: str) -> DrugCombinationsAssistantResponse:
            return await self.assistant_service.get_response(
                input_query=drug_name,
                prompt=Prompts.GET_DRUG_COMBINATIONS,
                pydantic_model=DrugCombinationsAssistantResponse
            )

    async def get_clear_researches(
            self,
            pubmed_researches_with_drug_name: ClearResearchesRequest
    ) -> DrugResearchesAssistantResponse:
        """
        Возвращает отфильтрованные исследования в лаконичном виде.
        :param pubmed_researches_with_drug_name: Схема с исследованиями и названием ДВ.
        :return: Схема с лаконичным видом исследований.
        """

        input_query = assistant_utils.serialize_researches_request(request=pubmed_researches_with_drug_name)
        return await self.get_response(
            input_query=input_query,
            prompt=Prompts.GET_DRUG_RESEARCHES,
            pydantic_model=DrugResearchesAssistantResponse,
        )

    async def get_user_description(self, user_name: str, user_drugs_name: str) -> AssistantResponseUserDescription:
        """
        Получить описание пользователя
        """
        user_query = user_name + ' ' + user_drugs_name
        return await self.get_response(input_query=user_query, prompt=Prompts.GET_USER_DESCRIPTION,
                                       pydantic_model=AssistantResponseUserDescription)

    async def get_user_query_validation(self, user_query: str) -> AssistantResponseDrugValidation:
        """
        ВАЛИДИРУЕТ ЗАПРОС ПОЛЬЗОВАТЕЛЯ НА РЕАЛЬНОСТЬ ПРЕПАРАТА.
        :param user_query: Запрос пользователя, предполагаемое название препарата
        :returns: AssistantResponseDrugValidation с правильным ДВ | с None
        """
        return await self.get_response(input_query=user_query, prompt=Prompts.DRUG_SEARCH_VALIDATION,
                                       pydantic_model=AssistantResponseDrugValidation, temperature=0.7)

    class PubMed:
        """Методы для работы с парсером"""

        def __init__(self, assistant_service):
            self.assistant_service = assistant_service

        async def get_pubmed_query(self, drug_name: str) -> AssistantResponsePubmedQuery:
            """
            Возвращает оптимизированный поисковой запрос для Pubmed исходя из названия действующего вещества.
            """
            return await self.assistant_service.get_response(
                input_query=drug_name,
                prompt=Prompts.GET_PUBMED_QUERY,
                pydantic_model=AssistantResponsePubmedQuery
            )

        async def get_pubmed_query_dosages(self, drug_name: str) -> AssistantResponsePubmedQuery:
            """
            Возвращает оптимизированный поисковой запрос для Pubmed исходя из названия действующего вещества.
            """
            return await self.assistant_service.get_response(
                input_query=drug_name,
                prompt=Prompts.GET_PUBMED_DOSAGES_QUERY,
                pydantic_model=AssistantResponsePubmedQuery
            )

        async def get_pubmed_query_mechanism(self, drug_name: str) -> AssistantResponsePubmedQuery:
            """
            Возвращает оптимизированный поисковой запрос для Pubmed исходя из названия действующего вещества.
            """
            return await self.assistant_service.get_response(
                input_query=drug_name,
                prompt=Prompts.GET_PUBMED_MECHANISM_QUERY,
                pydantic_model=AssistantResponsePubmedQuery
            )

        async def get_pubmed_query_metabolism(self, drug_name: str) -> AssistantResponsePubmedQuery:
            """
            Возвращает оптимизированный поисковой запрос для Pubmed исходя из названия действующего вещества.
            """
            return await self.assistant_service.get_response(
                input_query=drug_name,
                prompt=Prompts.GET_PUBMED_DOSAGES_QUERY,
                pydantic_model=AssistantResponsePubmedQuery
            )

    class Actions:
        """Действия пользователя

        Actions:

        drug_search | question | spam | other
        """

        def __init__(self, assistant_service):
            self.assistant_service = assistant_service

        async def predict_user_action(self, query: str) -> SelectActionResponse:
            """Предугадывает действие юзера с промптом"""
            return await self.assistant_service.get_response(
                input_query=query,
                prompt=Prompts.PREDICT_USER_ACTION,
                pydantic_model=SelectActionResponse,
                max_completion_tokens=50
            )

        async def answer_to_question(self, question: str, simple_mode: bool = False) -> QuestionAssistantResponse | None:
            """Отвечает на вопрос пользователя"""
            prompt = Prompts.ANSWER_TO_QUESTION
            if simple_mode:
                prompt += Prompts.ANSWER_TO_QUESTION_SIMPLE_PREFIX
            else:
                prompt += Prompts.ANSWER_TO_QUESTION_COMPLEX_PREFIX

            return await self.assistant_service.get_response(
                input_query=question,
                prompt=prompt,
                pydantic_model=QuestionAssistantResponse,
                max_completion_tokens=1550
            )

        async def answer_to_drugs_question(self, question: str) -> QuestionDrugsAssistantResponse:
            """Отвечает на вопрос пользователя и дает ему список препаратов для его решения"""
            return await self.assistant_service.get_response(
                input_query=question,
                prompt=Prompts.ANSWER_TO_DRUGS_QUESTION,
                pydantic_model=QuestionDrugsAssistantResponse
            )
