from datetime import date

from pydantic import BaseModel, Field

from typing import Optional


class PubmedResearchSchema(BaseModel):
    """Schema for representing PubMed research article data.

    Attributes:
        title (str): Title of the research article
        abstract (str): Abstract text of the article
        authors (str): List of authors with their affiliations
        doi (str): Digital Object Identifier for the article
        journal (str): Name of the journal where published
        publication_date (str): Date of publication (YYYY-MM-DD format)
        pubmed_id (str): PubMed unique identifier
        conclusion (Optional[str]): Conclusion section if available
        results (Optional[str]): Results section if available
    """
    title: str = Field(..., description="заголовок")
    abstract: Optional[str] = Field(None, description="краткое описание")
    authors: list[str] = Field(..., description="авторы")
    doi: str = Field(..., description="DOI")
    journal: str = Field(..., description="журнал")
    publication_date: date = Field(..., description="дата исследования")
    pubmed_id: str = Field(..., description="ID в PubMed")
    conclusion: Optional[str] = Field(None, description="заключение")
    results: Optional[str] = Field(None, description="результаты исследования")


class ClearResearchsRequest(BaseModel):
    """Схема для запроса к ассистенту для обработки исследований с парсера. Включает название препарата."""
    researchs: list[PubmedResearchSchema]
    drug_name: str = Field(..., description="Название действующего вещества")
