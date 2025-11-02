from datetime import date
from enum import Enum
from typing import Optional, Dict, List

from pydantic import BaseModel, Field

from drug_search.core.lexicon import EXIST_STATUS, DANGER_CLASSIFICATION
from drug_search.core.schemas.drug_schemas import DrugDosageSchema, DrugAnalogSchema, CombinationType, MechanismSummary, \
    Pathway, DrugCombinationSchema


class DosageRoute(str, Enum):
    parental = "parental"
    topical = "topical"
    other = "other"


class SelectActionResponse(BaseModel):
    action: str = Field(..., description="Тип действия пользователя")
    drug_name: Optional[str] = Field(None, description="Название препарата на английском")
    drug_name_ru: Optional[str] = Field(None, description="Название препарата на русском")
    drug_menu: Optional[str] = Field(None, description="Пункт меню препарата")


class QuestionDrugResponse(BaseModel):
    drug_name: str = Field(..., description="Действующее вещество")
    efficiency: str = Field(..., description="Процент эффективности в виде строки")
    description: str = Field(..., description="Описание препарата в контексте вопроса")


class QuestionAssistantResponse(BaseModel):
    answer: str = Field(..., description="Ответ на вопрос")
    drugs: List[QuestionDrugResponse] = Field(..., description="Список препаратов")


class AssistantResponseDrugValidation(BaseModel):
    status: EXIST_STATUS = Field(...)
    drug_name: str = Field(...)
    drug_name_ru: str = Field(...)
    danger_classification: DANGER_CLASSIFICATION = Field(...)


# [ DRUG CREATION ]
class DrugBrieflyAssistantResponse(BaseModel):
    drug_name: str = Field(..., description="Название ДВ на английском")
    drug_name_ru: str = Field(..., description="Название ДВ на русском")
    latin_name: Optional[str] = Field(None, description="Латинское название")
    synonyms: Optional[List[str]] = Field(None, description="Синонимы и коммерческие названия")
    description: Optional[str] = Field(None, description="Описание препарата")
    classification: Optional[str] = Field(None, description="Фармакологические классификации")
    danger_classification: DANGER_CLASSIFICATION = Field(...)
    fact: Optional[str] = Field(None, description="Интересный факт о препарате")


class DrugDosagesAssistantResponse(BaseModel):
    dosages:
    dosages_fun_fact: list[str] = Field(..., description="факты о дозировках")
    dosage_sources: list[str] = Field(..., description="источники дозировок")


class AssistantResponseCombinations(BaseModel):
    combinations: list[DrugCombinationSchema] = Field(...)


class AssistantResponseDrugPathways(BaseModel):
    pathways: list[Pathway] = Field(...)
    mechanism_summary: MechanismSummary = Field(...)
    pathway_sources: list[str] = Field(..., description="Источники по путям активации")


class AssistantResponseDrugResearch(BaseModel):
    name: str = Field(..., description="Название исследования")
    description: str = Field(..., description="Описание исследования")
    publication_date: date = Field(..., description="Дата публикации")
    url: str = Field(..., description="Ссылка на исследование")
    summary: Optional[str] = Field(None, description="Основной вывод")
    journal: str = Field(..., description="Название журнала")
    doi: str = Field(..., description="DOI статьи")
    authors: Optional[str] = Field(None, description="Авторы")
    study_type: Optional[str] = Field(None, description="Тип исследования")
    interest: float = Field(..., description="Оценка интереса 0.00-1.00")


class AssistantResponseDrugResearches(BaseModel):
    researches: list[AssistantResponseDrugResearch] = Field(...)


class AssistantResponsePubmedQuery(BaseModel):
    pubmed_query: str = Field(...)


class AssistantResponseUserDescription(BaseModel):
    user_description: str = Field(...)


class ClearResearchesRequest(BaseModel):
    drug_name: str = Field(...)
    researches: list[Dict] = Field(...)
