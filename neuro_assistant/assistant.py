import logging
from abc import ABC, abstractmethod
from typing import Union, Type

from dotenv import dotenv_values
from openai import OpenAI, APIError
from pydantic import ValidationError

from config import config
from core.exceptions import AssistantResponseError
from core.schemas.drug import AssistantDosageDescriptionResponse, AssistantResponseDrugPathway
from neuro_assistant.prompts import Prompts
from schemas.drug import AssistantResponseCombinations

env = dotenv_values(".env")

DEEPSEEK_API_KEY = env.get("DEEPSEEK_API_KEY")

logger = logging.getLogger("bot.assistant")

AssistantResponseModel = Union[
    AssistantResponseDrugPathway,
    AssistantDosageDescriptionResponse,
    AssistantResponseCombinations,
    ...
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
    def get_pathways(self) -> AssistantResponseDrugPathway:
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
        self.promptsClient = Prompts()

    def _get_response(
            self,
            drug_name: str,
            prompt: str,
            pydantic_model: Type[AssistantResponseModel]
    ):
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": f"{prompt}"},
                    {"role": "user", "content": f"{drug_name}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            if not response.choices:
                raise AssistantResponseError("ERROR: No data from assistant.")

            try:
                return pydantic_model.model_validate_json(response.choices[0].message.content)
            except ValidationError as e:
                raise ValueError(f"Invalid assistant response: {e}")

        except APIError as e:
            raise e
        except Exception:
            raise Exception

    def get_dosage(self, drug_name: str) -> AssistantDosageDescriptionResponse:
        return self._get_response(drug_name=drug_name, prompt=self.promptsClient.GET_DESCRIPTION_DOSAGES,
                                  pydantic_model=AssistantDosageDescriptionResponse)

    def get_pathways(self, drug_name: str) -> AssistantResponseDrugPathway:
        return self._get_response(drug_name=drug_name, prompt=self.promptsClient.GET_PATHWAY,
                                  pydantic_model=AssistantResponseDrugPathway)

    def get_combinations(self, drug_name: str) -> AssistantResponseCombinations:
        return self._get_response(drug_name=drug_name, prompt=self.promptsClient.GET_COMBINATIONS,
                                  pydantic_model=AssistantResponseCombinations)


assistant = Assistant(config.DEEPSEEK_API_KEY)

if __name__ == "__main__":
    print(assistant.get_pathways("парацетамол"))
    print()
