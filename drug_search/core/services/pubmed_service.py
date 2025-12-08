import asyncio
import threading
from typing import Optional

from pymed import PubMed

from drug_search.core.schemas import (AssistantResponsePubmedQuery, ClearResearchesRequest,
                                      DrugResearchesAssistantResponse, PubmedResearchSchema)
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
        Превращает словарь с ФИО в строку. Игнорирует поле affiliation.

        Возвращает массив со строками ФИО.
        """
        str_authors = []
        for author in authors:
            firstname = author["firstname"]
            lastname = author["lastname"]
            str_authors.append(f'{firstname} {lastname}')
        return str_authors

    async def __get_pubmed_query(self, drug_name: str) -> str:
        assistant_response: AssistantResponsePubmedQuery = await self.assistant_service.pubmed.get_pubmed_query(
            drug_name=drug_name)
        return assistant_response.pubmed_query

    async def get_pubmed_query_dosages(self, drug_name: str) -> str:
        assistant_response: AssistantResponsePubmedQuery = await self.assistant_service.pubmed.get_pubmed_query_dosages(
            drug_name=drug_name)
        return assistant_response.pubmed_query

    async def get_pubmed_query_mechanism(self, drug_name: str) -> str:
        assistant_response: AssistantResponsePubmedQuery = await self.assistant_service.pubmed.get_pubmed_query_mechanism(
            drug_name=drug_name)
        return assistant_response.pubmed_query

    async def get_pubmed_query_metabolism(self, drug_name: str) -> str:
        assistant_response: AssistantResponsePubmedQuery = await self.assistant_service.pubmed.get_pubmed_query_metabolism(
            drug_name=drug_name)
        return assistant_response.pubmed_query

    async def get_researches_dirty(self, drug_name: str) -> list[Optional[PubmedResearchSchema]]:
        """
        Возвращает исследования по препарату с помощью парсера PubMed.

        Сам оптимизирует запрос специфично для PubMed с помощью ассистента.
        :param drug_name: Действующее вещество препарата.
        """
        # Получаем все запросы параллельно
        pubmed_dosages_query, pubmed_mechanism_query, pubmed_metabolism_query = await asyncio.gather(
            self.get_pubmed_query_dosages(drug_name),
            self.get_pubmed_query_mechanism(drug_name),
            self.get_pubmed_query_metabolism(drug_name)
        )

        researches = []

        # Сначала пробуем найти исследования по специфичным запросам
        for query in [pubmed_dosages_query, pubmed_mechanism_query, pubmed_metabolism_query]:
            self._process_articles_from_query(query, researches, max_articles=50)

        # Если специфичных исследований нет, ищем любые исследования
        if not researches:
            pubmed_query = await self.__get_pubmed_query(drug_name)
            self._process_articles_from_query(pubmed_query, researches, max_articles=50)

        return researches

    def _process_articles_from_query(self, query: str, researches: list, max_articles: int) -> None:
        """Обрабатывает статьи из PubMed запроса и добавляет их в список исследований."""
        pubmed_articles = self.pubmed.query(query=query, max_results=100)
        count = 0

        for pubmed_article in pubmed_articles:
            if count >= max_articles:
                break

            if not self._is_valid_article(pubmed_article):
                continue

            if pubmed_article.doi in (research.doi for research in researches):
                continue

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
            count += 1

    def _is_valid_article(self, pubmed_article) -> bool:
        """Проверяет валидность статьи PubMed."""
        if not pubmed_article:
            return False

        if "\n" in str(pubmed_article.doi) or "\n" in str(pubmed_article.pubmed_id):
            return False

        if not pubmed_article.doi or not pubmed_article.pubmed_id:
            return False

        return True

    async def get_researches_clearly(self, drug_name: str) -> DrugResearchesAssistantResponse:
        """Возвращает исследования в красивом виде после обработки ИИ"""
        researches: list[Optional[PubmedResearchSchema]] = await self.get_researches_dirty(
            drug_name=drug_name
        )
        researches_request_to_assistant = ClearResearchesRequest(
            researches=researches,
            drug_name=drug_name
        )

        clear_researches: DrugResearchesAssistantResponse = await self.assistant_service.get_clear_researches(
            researches_request_to_assistant
        )
        return clear_researches
