from typing import Optional

from pymed import PubMed

from drug_search.core.schemas import AssistantResponsePubmedQuery
from drug_search.core.schemas.pubmed_schema import PubmedResearchSchema
from drug_search.core.services import Assistant


class PubmedParser:
    def __init__(self):
        self.pubmed = PubMed()

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

    @staticmethod
    def __get_pubmed_query(drug_name: str, assistant_service: Assistant) -> str:
        assistant_response: AssistantResponsePubmedQuery = assistant_service.get_pubmed_query(drug_name=drug_name)
        return assistant_response.pubmed_query

    def get_researches(self, drug_name: str, assistant_service: Assistant) -> list[Optional[PubmedResearchSchema]]:
        """
        Возвращает исследования по препарату с помощью парсера PubMed.

        Сам оптимизирует запрос специфично для PubMed с помощью ассистента.

        :param assistant_service: экземпляр сервиса ассистента
        :param drug_name: Действующее вещество препарата.
        """
        pubmed_query: str = self.__get_pubmed_query(drug_name=drug_name, assistant_service=assistant_service)
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


pubmed_parser = PubmedParser()


def get_pubmed_parser():
    """Return singletone object"""
    return pubmed_parser
