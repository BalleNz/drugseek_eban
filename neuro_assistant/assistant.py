import json
import logging
from abc import ABC, abstractmethod
from typing import Union, Type, Optional

from dotenv import dotenv_values
from openai import OpenAI, APIError
from pydantic import ValidationError

from config import config
from schemas import AssistantResponseDrugResearchs, AssistantResponsePubmedQuery
from schemas.pubmed_schema import PubmedResearchSchema, ClearResearchsRequest
from utils.exceptions import AssistantResponseError
from schemas.assistant_responses import AssistantDosageDescriptionResponse, AssistantResponseCombinations, \
    AssistantResponseDrugPathways, AssistantResponseDrugValidation
from neuro_assistant.prompts import Prompts

env = dotenv_values(".env")

DEEPSEEK_API_KEY = env.get("DEEPSEEK_API_KEY")

logger = logging.getLogger("bot.assistant")

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
    def get_pathways(self) -> AssistantResponseDrugPathways:
        """Возвращает все пути активации."""
        ...

    @abstractmethod
    def get_best_price(self) -> dict:
        """Возвращает лучшие цены и ссылки на покупку."""
        ...

    @abstractmethod
    def get_synergists(self) -> dict:
        """Возвращает хорошие и негативные комбинации с описанием эффектов."""
        ...


class Assistant():
    def __init__(self, DEEPSEEK_API_KEY: str):
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        self.prompts = Prompts()

    def get_response(
            self,
            input_query: str,
            prompt: str,
            pydantic_model: Type[AssistantResponseModel]
    ):
        # TODO: обработка нулевого баланса (отдельный метод)
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": f"{prompt}"},
                    {"role": "user", "content": f"{input_query}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            if not response.choices:
                raise AssistantResponseError("ERROR: No data from assistant.")

            try:
                if pydantic_model:
                    return pydantic_model.model_validate_json(response.choices[0].message.content)

                # если нет Pydantic модели —> возращает строку.
                return response.choices[0].message.content
            except ValidationError as e:
                raise ValueError(f"Invalid assistant response: {e}")

        except APIError as e:
            raise e
        except Exception as ex:
            raise Exception

    def get_dosage(self, drug_name: str) -> AssistantDosageDescriptionResponse:
        return self.get_response(input_query=drug_name, prompt=self.prompts.GET_DRUG_DESCRIPTION,
                                 pydantic_model=AssistantDosageDescriptionResponse)

    def get_pathways(self, drug_name: str) -> AssistantResponseDrugPathways:
        return self.get_response(input_query=drug_name, prompt=self.prompts.GET_DRUG_PATHWAYS,
                                 pydantic_model=AssistantResponseDrugPathways)

    def get_combinations(self, drug_name: str) -> AssistantResponseCombinations:
        return self.get_response(input_query=drug_name, prompt=self.prompts.GET_DRUG_SYNERGISTS,
                                 pydantic_model=AssistantResponseCombinations)

    def get_user_description(self, user_name: str, user_drug_names: list[str]) -> ...:
        user_drug_names_text = ', '.join(user_drug_names)
        user_query = user_name + ' ' + user_drug_names_text
        return self.get_response(input_query=user_query, prompt=self.prompts.GET_USER_DESCRIPTION,
                                 pydantic_model=None)

    def get_user_query_validation(self, user_query: str) -> AssistantResponseDrugValidation:
        return self.get_response(input_query=user_query, prompt=self.prompts.DRUG_SEARCH_VALIDATION,
                                 pydantic_model=AssistantResponseDrugValidation)

    def get_clear_researchs(self, pubmed_researchs_with_drug_name: ClearResearchsRequest) -> AssistantResponseDrugResearchs:
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


assistant = Assistant(config.DEEPSEEK_API_KEY)

if __name__ == "__main__":
    print(assistant.get_pathways("парацетамол"))
    print()
