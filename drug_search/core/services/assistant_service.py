import json
import logging
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Union, Type, AsyncGenerator, Sequence

from openai import OpenAI, APIError
from pydantic import ValidationError

from drug_search.config import config
from drug_search.core.schemas import (AssistantResponseDrugResearchs, AssistantResponsePubmedQuery,
                                      AssistantDosageDescriptionResponse, AssistantResponseCombinations,
                                      AssistantResponseDrugPathways, AssistantResponseDrugValidation,
                                      ClearResearchesRequest)
from drug_search.core.utils.exceptions import AssistantResponseError
from drug_search.core.lexicon import Prompts

logger = logging.getLogger(__name__)

AssistantResponseModel = Union[
    AssistantResponseDrugPathways,
    AssistantDosageDescriptionResponse,
    AssistantResponseCombinations,
    AssistantResponseDrugValidation,
    AssistantResponseDrugResearchs,
    None,
]


class AssistantInterface(ABC):
    @abstractmethod
    def get_dosage(self, drug_name) -> AssistantDosageDescriptionResponse:
        """
        Первый запрос для нового препарата.
        Возвращает рекомендуемые дозировки препарата для разных способов приема + описание.
        """
        ...

    @abstractmethod
    def get_pathways(self, drug_name: str) -> AssistantResponseDrugPathways:
        """Возвращает все пути активации."""
        ...

    @abstractmethod
    def get_synergists(self, drug_name: str) -> dict:
        """Возвращает хорошие и негативные комбинации с описанием эффектов."""
        ...


class Assistant(AssistantInterface):
    def __init__(self):
        self.prompts = Prompts()
        self.client = None

    async def __aenter__(self):
        self.client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.close()

    def get_response(
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
                logger.error(f"Raw response: {response.choices[0].message.content}\n\n"
                             f"Model: {pydantic_model}")
                raise ValueError(f"Invalid assistant response: {e}")

        except APIError as e:
            raise e
        except Exception as ex:
            raise ex

    def get_dosage(self, drug_name: str) -> AssistantDosageDescriptionResponse:
        return self.get_response(input_query=drug_name, prompt=self.prompts.GET_DRUG_DESCRIPTION,
                                 pydantic_model=AssistantDosageDescriptionResponse)

    def get_pathways(self, drug_name: str) -> AssistantResponseDrugPathways:
        return self.get_response(input_query=drug_name, prompt=self.prompts.GET_DRUG_PATHWAYS,
                                 pydantic_model=AssistantResponseDrugPathways)

    def get_synergists(self, drug_name: str) -> AssistantResponseCombinations:
        return self.get_response(input_query=drug_name, prompt=self.prompts.GET_DRUG_COMBINATIONS,
                                 pydantic_model=AssistantResponseCombinations)

    def get_user_description(self, user_name: str, user_drug_names: Sequence[str]) -> ...:
        user_drug_names_text = ', '.join(user_drug_names)
        user_query = user_name + ' ' + user_drug_names_text
        return self.get_response(input_query=user_query, prompt=self.prompts.GET_USER_DESCRIPTION,
                                 pydantic_model=None)

    def get_user_query_validation(self, user_query: str) -> AssistantResponseDrugValidation:
        """
        ВАЛИДИРУЕТ ЗАПРОС ПОЛЬЗОВАТЕЛЯ НА РЕАЛЬНОСТЬ ПРЕПАРАТА.
        :param user_query: Запрос пользователя, предполагаемое название препарата
        :returns: AssistantResponseDrugValidation с правильным ДВ | с None
        """
        return self.get_response(input_query=user_query, prompt=self.prompts.DRUG_SEARCH_VALIDATION,
                                 pydantic_model=AssistantResponseDrugValidation)

    def get_clear_researchs(self,
                            pubmed_researchs_with_drug_name: ClearResearchesRequest) -> AssistantResponseDrugResearchs:
        """
        Возвращает отфильтрованные исследования в лаконичном виде.
        :param pubmed_researchs_with_drug_name: Схема с исследованиями и названием ДВ.
        :return: Схема с лаконичным видом исследований.
        """

        def get_raw_researchs_request_from_pydantic() -> str:
            """Превращение Pydantic схемы в строку"""
            json_query = {
                "drug_name": pubmed_researchs_with_drug_name.drug_name,
                "researchs": [
                    {
                        **research.model_dump(exclude_none=True),
                        "publication_date": research.publication_date.isoformat()
                    }
                    for research in pubmed_researchs_with_drug_name.researchs
                ]
            }
            return json.dumps(json_query, indent=4, ensure_ascii=False)

        input_query = get_raw_researchs_request_from_pydantic()
        return self.get_response(input_query=input_query, prompt=self.prompts.GET_DRUG_RESEARCHS,
                                 pydantic_model=AssistantResponseDrugResearchs)

    def get_pubmed_query(self, drug_name: str) -> str:
        """
        Возвращает оптимизированный поисковой запрос для Pubmed исходя из названия действующего вещества.
        """
        return self.get_response(input_query=drug_name, prompt=self.prompts.GET_PUBMED_SEARCH_QUERY,
                                 pydantic_model=AssistantResponsePubmedQuery)


@asynccontextmanager
async def get_assistant() -> AsyncGenerator[Assistant, None]:
    assistant: Assistant = Assistant()
    try:
        yield assistant
    finally:
        assistant.client.close()
