from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field

from drug_search.core.lexicon import EXIST_STATUS, DANGER_CLASSIFICATION
from drug_search.core.schemas.drug_schemas import DrugDosageSchema, DrugAnalogSchema, MechanismSummary, \
    DrugPathwaySchema, DrugCombinationSchema, DrugResearchSchema, MetabolismPhase, Pharmacokinetics, EliminationInfo


class DosageRoute(str, Enum):
    parental = "parental"
    topical = "topical"
    other = "other"


# [ DRUG CREATION ]

class DrugBrieflyAssistantResponse(BaseModel):
    """
    prompt: GET_DRUG_BRIEFLY_INFO
    """
    drug_name: str = Field(..., description="Название ДВ на английском")
    drug_name_ru: str = Field(..., description="Название ДВ на русском")
    latin_name: Optional[str] = Field(None, description="Латинское название")
    synonyms: Optional[List[str]] = Field(None, description="Синонимы и коммерческие названия")
    description: Optional[str] = Field(None, description="Описание препарата")
    classification: Optional[str] = Field(None, description="Фармакологические классификации")
    danger_classification: DANGER_CLASSIFICATION = Field(..., description="класс опасности препарата")
    fact: Optional[str] = Field(None, description="Интересный факт о препарате")
    fun_facts: list[str] = Field(..., description="факты о дозировках")


class DrugDosagesAssistantResponse(BaseModel):
    """
    prompt: GET_DRUG_DOSAGES
    """
    dosages: list[DrugDosageSchema] = Field(..., description="дозировки")
    dosage_sources: list[str] = Field(..., description="источники дозировок")


class DrugAnalogsAssistantResponse(BaseModel):
    """
    prompt: GET_DRUG_ANALOGS
    """
    analogs: list[DrugAnalogSchema] = Field(..., description="аналоги")
    analogs_description: str | None = Field(..., description="описание аналогов")


class DrugMetabolismAssistantResponse(BaseModel):
    """
    prompt: GET_DRUG_METABOLISM
    """
    pharmacokinetics: list[Pharmacokinetics] = Field(..., description="фармакокинетика")
    metabolism: list[MetabolismPhase] = Field(..., description="метаболизм")
    metabolism_description: str = Field(..., description="описание метаболизма")
    elimination: list[EliminationInfo] = Field(..., description="выведение")


class DrugPathwaysAssistantResponse(BaseModel):
    """
    Ответ на
     GET_DRUG_PATHWAYS
    """
    pathways: list[DrugPathwaySchema] = Field(...)
    mechanism_summary: MechanismSummary = Field(...)
    pathway_sources: list[str] = Field(..., description="Источники по путям активации")


class DrugCombinationsAssistantResponse(BaseModel):
    """
    Ответ на
     GET_DRUG_COMBINATIONS
    """
    combinations: list[DrugCombinationSchema] = Field(...)


class DrugResearchesAssistantResponse(BaseModel):
    """
    Ответ на
     GET_DRUG_RESEARCHES
    """
    researches: list[DrugResearchSchema] = Field(...)


# [ OTHER ]

class AssistantResponsePubmedQuery(BaseModel):
    pubmed_query: str = Field(...)


class AssistantResponseUserDescription(BaseModel):
    user_description: str = Field(...)


"""class SelectActionResponse(BaseModel):
    action: str = Field(..., description="Тип действия пользователя")
    drug_name: Optional[str] = Field(None, description="Название препарата на английском")
    drug_name_ru: Optional[str] = Field(None, description="Название препарата на русском")
    drug_menu: DrugMenu | None = Field(None, description="Пункт меню препарата")"""


class QuestionDrugResponse(BaseModel):
    drug_name: str = Field(..., description="Действующее вещество")
    efficiency: str = Field(..., description="Процент эффективности в виде строки")
    description: str = Field(..., description="Описание препарата в контексте вопроса")


class QuestionAssistantResponse(BaseModel):
    answer: str = Field(..., description="Ответ на вопрос c HTML тегами")


class QuestionDrugsAssistantResponse(BaseModel):
    answer: str = Field(..., description="Ответ на вопрос")
    drugs: List[QuestionDrugResponse] = Field(..., description="Список препаратов")


class AssistantResponseDrugValidation(BaseModel):
    status: EXIST_STATUS = Field(...)
    drug_name: str = Field(...)
    drug_name_ru: str = Field(...)
    danger_classification: DANGER_CLASSIFICATION = Field(...)
