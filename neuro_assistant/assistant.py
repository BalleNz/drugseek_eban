import logging
from abc import ABC, abstractmethod
from typing import Union, Type

from dotenv import dotenv_values
from openai import OpenAI, APIError
from pydantic import ValidationError

from config import config
from utils.exceptions import AssistantResponseError
from schemas.assistant_responses import AssistantDosageDescriptionResponse, AssistantResponseCombinations, \
    AssistantResponseDrugPathway, AssistantResponseDrugValidation
from neuro_assistant.prompts import Prompts

env = dotenv_values(".env")

DEEPSEEK_API_KEY = env.get("DEEPSEEK_API_KEY")

logger = logging.getLogger("bot.assistant")

AssistantResponseModel = Union[
    AssistantResponseDrugPathway,
    AssistantDosageDescriptionResponse,
    AssistantResponseCombinations,
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

    def get_response(
            self,
            user_query: str,
            prompt: str,
            pydantic_model: Type[AssistantResponseModel]
    ):
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": f"{prompt}"},
                    {"role": "user", "content": f"{user_query}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            if not response.choices:
                raise AssistantResponseError("ERROR: No data from assistant.")

            try:
                if pydantic_model:
                    return pydantic_model.model_validate_json(response.choices[0].message.content)
                return response.choices[0].message.content
            except ValidationError as e:
                raise ValueError(f"Invalid assistant response: {e}")

        except APIError as e:
            raise e
        except Exception:
            raise Exception

    def get_dosage(self, drug_name: str) -> AssistantDosageDescriptionResponse:
        return self.get_response(user_query=drug_name, prompt=self.promptsClient.GET_DRUG_DESCRIPTION,
                                 pydantic_model=AssistantDosageDescriptionResponse)

    def get_pathways(self, drug_name: str) -> AssistantResponseDrugPathway:
        return self.get_response(user_query=drug_name, prompt=self.promptsClient.GET_DRUG_PATHWAYS,
                                 pydantic_model=AssistantResponseDrugPathway)

    def get_combinations(self, drug_name: str) -> AssistantResponseCombinations:
        return self.get_response(user_query=drug_name, prompt=self.promptsClient.GET_DRUG_SYNERGISTS,
                                 pydantic_model=AssistantResponseCombinations)

    def get_user_description(self, user_name: str, user_drug_names: list[str]):
        user_drug_names_text = ', '.join(user_drug_names)
        user_query = user_name + ' ' + user_drug_names_text
        return self.get_response(user_query=user_query, prompt=self.promptsClient.GET_USER_DESCRIPTION,
                                 pydantic_model=None)

    def get_user_query_validation(self, user_query: str):
        return self.get_response(user_query=user_query, prompt=self.promptsClient.DRUG_SEARCH_VALIDATION,
                                 pydantic_model=AssistantResponseDrugValidation)


assistant = Assistant(config.DEEPSEEK_API_KEY)

if __name__ == "__main__":
    print(assistant.get_pathways("парацетамол"))
    print()
