import logging
from abc import ABC, abstractmethod
from typing import Union

from dotenv import dotenv_values
from openai import OpenAI, APIError
from pydantic import ValidationError

from config import config
from core.schemas.drug import AssistantDosageResponse
from neuro_assistant.prompts import Prompts

env = dotenv_values("../.env")

DEEPSEEK_API_KEY = env.get("DEEPSEEK_API_KEY")

logger = logging.getLogger("bot.assistant")


class AssistantInterface(ABC):
    @abstractmethod
    def get_dosage(self, drug_name) -> dict:
        """Возвращает рекомендуемые дозировки препарата для разных способов приема"""
        ...

    @abstractmethod
    def get_pathways(self) -> dict:
        """Возвращает все пути активации"""
        ...

    @abstractmethod
    def get_best_price(self) -> dict:
        """Возвращает лучшие цены и ссылки на покупку"""
        ...

    @abstractmethod
    def get_synergists(self) -> dict:
        """Возвращает хорошие и негативные комбинации с описанием эффектов"""
        ...


class Assistant():
    def __init__(self, DEEPSEEK_API_KEY: str):
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        self.promptsClient = Prompts()

    def get_dosage(self, drug_name) -> Union[AssistantDosageResponse, dict]:
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self.promptsClient.GET_DOSAGES},
                    {"role": "user", "content": f"{drug_name}"}],
                response_format={"type": "json_object"},
                temperature=0.3,
            )

            if not response.choices:
                return {"error": "No choices in API response"}

            try:
                return AssistantDosageResponse.model_validate_json(response.choices[0].message.content)
            except ValidationError as e:
                raise ValueError(f"Invalid assistant response: {e}")
        except APIError as e:
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}


assistant = Assistant(config.DEEPSEEK_API_KEY)
