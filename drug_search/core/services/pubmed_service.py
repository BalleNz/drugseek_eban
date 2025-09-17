import threading
from typing import Optional

from pymed import PubMed

from drug_search.core.schemas import (AssistantResponsePubmedQuery, ClearResearchesRequest,
                                      AssistantResponseDrugResearches, PubmedResearchSchema, AssistantResponseDrugResearch)
from drug_search.core.services.assistant_service import AssistantService


class PubmedService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, assistant_service: AssistantService):
        with self._lock:
            if not self._initialized:
                self.pubmed = PubMed()
                self.assistant_service = assistant_service
                self._initialized = True

    @staticmethod
    def __parse_authors(authors: dict) -> list[str]:
        """
        Превращает словарь с ФИО в строку. Игнорирует поле affilation.

        Возращает массив со строками ФИО.
        """
        str_authors = []
        for author in authors:
            firstname = author["firstname"]
            lastname = author["lastname"]
            str_authors.append(f'{firstname} {lastname}')
        return str_authors

    async def get_pubmed_query(self, drug_name: str) -> str:
        assistant_response: AssistantResponsePubmedQuery = await self.assistant_service.get_pubmed_query(
            drug_name=drug_name)
        return assistant_response.pubmed_query

    async def get_researches_dirty(self, drug_name: str) -> list[Optional[PubmedResearchSchema]]:
        """
        Возвращает исследования по препарату с помощью парсера PubMed.

        Сам оптимизирует запрос специфично для PubMed с помощью ассистента.
        :param drug_name: Действующее вещество препарата.
        """
        pubmed_query: str = await self.get_pubmed_query(drug_name=drug_name)
        pubmed_articles = self.pubmed.query(query=pubmed_query, max_results=100)

        researches: list[Optional[PubmedResearchSchema, None]] = []

        for pubmed_article in pubmed_articles:
            # пропуск артиклей с несколькими doi и pubmed_id
            try:
                if "\n" in pubmed_article.doi or "\n" in pubmed_article.pubmed_id:
                    continue
            except TypeError:
                # Заканчивает цикл, если итерация пустая
                break

            researches.append(
                PubmedResearchSchema(
                    title=pubmed_article.title,
                    abstract=pubmed_article.abstract,
                    authors=self.__parse_authors(pubmed_article.authors),
                    doi=pubmed_article.doi,
                    journal=pubmed_article.journal,
                    publication_date=pubmed_article.publication_date,
                    pubmed_id=pubmed_article.pubmed_id,
                    conclusion=pubmed_article.conclusions,
                    results=pubmed_article.results
                )
            )
        return researches[:10]  # первые 10 исследований, чтобы не перегружать нейронку

    async def get_researches_clearly(self, drug_name: str) -> list[AssistantResponseDrugResearch]:
        """Возвращает исследования в красивом виде после обработки ИИ"""
        researches: list[Optional[PubmedResearchSchema]] = await self.get_researches_dirty(
            drug_name=drug_name
        )
        researches_request_to_assistant = ClearResearchesRequest(
            researches=researches,
            drug_name=drug_name
        )

        clear_researches: AssistantResponseDrugResearches = await self.assistant_service.get_clear_researches(
            researches_request_to_assistant)
        return clear_researches.researches
