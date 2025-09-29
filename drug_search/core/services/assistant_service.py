import json
import logging
import threading
from abc import ABC, abstractmethod
from typing import Union, Type, Sequence

from openai import OpenAI, APIError
from pydantic import ValidationError

from drug_search.config import config
from drug_search.core.lexicon import Prompts
from drug_search.core.schemas import (AssistantResponseDrugResearches, AssistantResponsePubmedQuery,
                                      AssistantDosageDescriptionResponse, AssistantResponseCombinations,
                                      AssistantResponseDrugPathways, AssistantResponseDrugValidation,
                                      ClearResearchesRequest, SelectActionResponse)
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
                self.prompts = Prompts()
                self.client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
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

                # если нет Pydantic модели —> возращает строку.
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
        return await self.get_response(input_query=drug_name, prompt=self.prompts.GET_DRUG_DESCRIPTION,
                                       pydantic_model=AssistantDosageDescriptionResponse)

    async def get_pathways(self, drug_name: str) -> AssistantResponseDrugPathways:
        return await self.get_response(input_query=drug_name, prompt=self.prompts.GET_DRUG_PATHWAYS,
                                       pydantic_model=AssistantResponseDrugPathways)

    async def get_synergists(self, drug_name: str) -> AssistantResponseCombinations:
        return await self.get_response(input_query=drug_name, prompt=self.prompts.GET_DRUG_COMBINATIONS,
                                       pydantic_model=AssistantResponseCombinations)

    async def get_user_description(self, user_name: str, user_drug_names: Sequence[str]) -> ...:
        user_drug_names_text = ', '.join(user_drug_names)
        user_query = user_name + ' ' + user_drug_names_text
        return await self.get_response(input_query=user_query, prompt=self.prompts.GET_USER_DESCRIPTION,
                                       pydantic_model=None)

    async def get_user_query_validation(self, user_query: str) -> AssistantResponseDrugValidation:
        """
        ВАЛИДИРУЕТ ЗАПРОС ПОЛЬЗОВАТЕЛЯ НА РЕАЛЬНОСТЬ ПРЕПАРАТА.
        :param user_query: Запрос пользователя, предполагаемое название препарата
        :returns: AssistantResponseDrugValidation с правильным ДВ | с None
        """
        return await self.get_response(input_query=user_query, prompt=self.prompts.DRUG_SEARCH_VALIDATION,
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

        def get_raw_researchs_request_from_pydantic() -> str:
            """Превращение Pydantic схемы в строку"""
            json_query = {
                "drug_name": pubmed_researches_with_drug_name.drug_name,
                "researches": [
                    {
                        **research.model_dump(exclude_none=True),
                        "publication_date": research.publication_date.isoformat()
                    }
                    for research in pubmed_researches_with_drug_name.researches
                ]
            }
            return json.dumps(json_query, indent=4, ensure_ascii=False)

        input_query = get_raw_researchs_request_from_pydantic()
        return await self.get_response(input_query=input_query, prompt=self.prompts.GET_DRUG_RESEARCHES,
                                       pydantic_model=AssistantResponseDrugResearches)

    async def get_pubmed_query(self, drug_name: str) -> AssistantResponsePubmedQuery:
        """
        Возвращает оптимизированный поисковой запрос для Pubmed исходя из названия действующего вещества.
        """
        return await self.get_response(input_query=drug_name, prompt=self.prompts.GET_PUBMED_SEARCH_QUERY,
                                       pydantic_model=AssistantResponsePubmedQuery)

    async def predict_user_action(self, query: str) -> SelectActionResponse:
        """Предугадывает действие юзера с промптом"""
        return await self.get_response(
            input_query=query,
            prompt=self.prompts.PREDICT_USER_ACTION,
            pydantic_model=SelectActionResponse
        )
