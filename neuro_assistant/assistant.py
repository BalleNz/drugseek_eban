from abc import ABC, abstractmethod
from dotenv import dotenv_values
from openai import OpenAI

from neuro_assistant.prompts import Prompts

env = dotenv_values("../.env")

DEEPSEEK_API_KEY = env.get("DEEPSEEK_API_KEY")


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


class Assistant(AssistantInterface):
    def __init__(self, DEEPSEEK_API_KEY: str):
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        self.promptsClient = Prompts()

    def get_dosage(self, drug_name) -> dict:
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": self.promptsClient.GET_DOSAGES},
                {"role": "user", "content": f"{drug_name}"}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        return response.choices[0].message.content


print(Assistant(DEEPSEEK_API_KEY).get_dosage("Тестостерон ундеконат"))
