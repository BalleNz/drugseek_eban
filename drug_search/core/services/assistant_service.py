import logging
import threading
from abc import ABC, abstractmethod
from typing import Union, Type

from openai import OpenAI, APIError
from pydantic import ValidationError

from drug_search.config import config
from drug_search.core.lexicon import Prompts
from drug_search.core.schemas import (AssistantResponseDrugResearches, AssistantResponsePubmedQuery,
                                      AssistantDosageDescriptionResponse, AssistantResponseCombinations,
                                      AssistantResponseDrugPathways, AssistantResponseDrugValidation,
                                      ClearResearchesRequest, SelectActionResponse, QuestionAssistantResponse,
                                      AssistantResponseUserDescription)
from drug_search.core.utils import assistant_utils
from drug_search.core.utils.exceptions import AssistantResponseError

logger = logging.getLogger(__name__)

AssistantResponseModel = Union[
    AssistantResponseDrugPathways,
    AssistantDosageDescriptionResponse,
    AssistantResponseCombinations,
    AssistantResponseDrugValidation,
    AssistantResponseDrugResearches,
    None,
]


class AssistantInterface(ABC):
    @abstractmethod
    async def get_dosage(self, drug_name) -> AssistantDosageDescriptionResponse:
        """
        Первый запрос для нового препарата.
        Возвращает рекомендуемые дозировки препарата для разных способов приема + описание.
        """
        ...

    @abstractmethod
    async def get_pathways(self, drug_name: str) -> AssistantResponseDrugPathways:
        """Возвращает все пути активации."""
        ...

    @abstractmethod
    async def get_synergists(self, drug_name: str) -> dict:
        """Возвращает хорошие и негативные комбинации с описанием эффектов."""
        ...


class AssistantService(AssistantInterface):
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        with self._lock:
            if not self._initialized:
                self.client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
                self.actions = self.UserActions(self)
                self._initialized = True

    async def get_response(
            self,
            input_query: str,
            prompt: str,
            pydantic_model: Type[AssistantResponseModel],
            temperature: float = 0.3
    ):
        # TODO: обработка нулевого баланса (отдельный метод) + Обработка если дипсик не работает (server is busy)
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": f"{prompt}"},
                    {"role": "user", "content": f"{input_query}"}
                ],
                response_format={"type": "json_object"},
                temperature=temperature
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

        except APIError as e:
            raise e
        except Exception as ex:
            raise ex

    async def get_dosage(self, drug_name: str) -> AssistantDosageDescriptionResponse:
        return await self.get_response(input_query=drug_name, prompt=Prompts.GET_DRUG_DESCRIPTION,
                                       pydantic_model=AssistantDosageDescriptionResponse)

    async def get_pathways(self, drug_name: str) -> AssistantResponseDrugPathways:
        return await self.get_response(input_query=drug_name, prompt=Prompts.GET_DRUG_PATHWAYS,
                                       pydantic_model=AssistantResponseDrugPathways)

    async def get_synergists(self, drug_name: str) -> AssistantResponseCombinations:
        return await self.get_response(input_query=drug_name, prompt=Prompts.GET_DRUG_COMBINATIONS,
                                       pydantic_model=AssistantResponseCombinations)

    async def get_user_description(self, user_name: str, user_drugs_name: str) -> AssistantResponseUserDescription:
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

    async def get_clear_researches(
            self,
            pubmed_researches_with_drug_name: ClearResearchesRequest
    ) -> AssistantResponseDrugResearches:
        """
        Возвращает отфильтрованные исследования в лаконичном виде.
        :param pubmed_researches_with_drug_name: Схема с исследованиями и названием ДВ.
        :return: Схема с лаконичным видом исследований.
        """

        input_query = assistant_utils.serialize_researches_request(request=pubmed_researches_with_drug_name)
        return await self.get_response(input_query=input_query, prompt=Prompts.GET_DRUG_RESEARCHES,
                                       pydantic_model=AssistantResponseDrugResearches)

    async def get_pubmed_query(self, drug_name: str) -> AssistantResponsePubmedQuery:
        """
        Возвращает оптимизированный поисковой запрос для Pubmed исходя из названия действующего вещества.
        """
        return await self.get_response(input_query=drug_name, prompt=Prompts.GET_PUBMED_SEARCH_QUERY,
                                       pydantic_model=AssistantResponsePubmedQuery)

    class UserActions:
        """Класс для взаимодействием с действиями пользователя:

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
                pydantic_model=SelectActionResponse
            )

        async def answer_to_question(self, question: str) -> QuestionAssistantResponse:
            """Отвечает на вопрос пользователя и дает ему список препаратов для его решения"""
            return await self.assistant_service.get_response(
                input_query=question,
                prompt=Prompts.ANSWER_TO_DRUGS_QUESTION,
                pydantic_model=QuestionAssistantResponse
            )
