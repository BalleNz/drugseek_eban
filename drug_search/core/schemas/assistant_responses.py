from datetime import date
from enum import Enum
from typing import Optional, Dict

from pydantic import BaseModel, Field

from drug_search.core.schemas.drug_schemas import DrugAnalogSchemaRequest, Pharmacokinetics, Pathway, MechanismSummary, \
    CombinationType


class EXIST_STATUS(Enum):
    EXIST: str = "exist"
    NOT_EXIST: str = "not exist"


class DosageParams(BaseModel):
    """Параметры дозировки для ответа ассистента"""
    per_time: Optional[str] = Field(default=None)
    max_day: Optional[str] = Field(default=None)
    per_time_weight_based: Optional[str] = Field(default=None)
    max_day_weight_based: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class AssistantResponseDrugValidation(BaseModel):
    status: EXIST_STATUS = Field(...)
    drug_name: str = Field(default=None)


class AssistantDosageDescriptionResponse(BaseModel):
    """Ответ ИИ по дозировкам и описанию препарата"""
    drug_name: str = Field(..., description="одно возможное название для ДВ на англ.")
    latin_name: str = Field(...)
    drug_name_ru: str = Field(...)

    synonyms: Optional[list[str]] = Field(None, description="все возможные названия для препарата на RU")

    analogs: Optional[list[DrugAnalogSchemaRequest]] = Field(None, description="аналоги препарата")
    dosages_fun_fact: Optional[str] = Field(default=None)
    description: str = Field(...)
    classification: str = Field(...)
    sources: list[str] = Field(...)

    pharmacokinetics: Pharmacokinetics

    is_danger: bool = Field(...)

    dosages: Dict[str, Optional[Dict[str, Optional[DosageParams]]]]

    class Config:
        validate_by_name = True


class AssistantResponseDrugCombinationSchema(BaseModel):
    combination_type: CombinationType
    substance: str = Field(..., description="ДВ")
    effect: str
    products: Optional[list[str]] = Field(default=None)  # only for good
    risks: Optional[str] = Field(default=None)  # only for bad
    sources: list[str]


class AssistantResponseCombinations(BaseModel):
    combinations: list[AssistantResponseDrugCombinationSchema]


class AssistantResponseDrugPathways(BaseModel):
    pathways: list[Pathway]
    mechanism_summary: MechanismSummary

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "pathways": [{
                    "receptor": "α2A-адренорецептор",
                    "binding_affinity": "Ki = 2.1 нМ",
                    "affinity_description": "очень сильное связывание",
                    "activation_type": "антагонист",
                    "pathway": "Gi/o protein cascade",
                    "effect": "повышение норадреналина"
                }],
                "mechanism_summary": {
                    "primary_action": "блокада α2-адренорецепторов",
                    "secondary_actions": ["агонизм 5-HT1A", "антагонизм D2"],
                    "clinical_effects": ["усиление либидо", "повышение АД", "тревожность"]
                },
                "sources": ["DrugBank", "PubChem", "IUPHAR"]
            }
        }


class AssistantResponseDrugResearch(BaseModel):
    name: str = Field(..., description="название исследования")
    description: str = Field(..., description="описание исследования")
    publication_date: date = Field(..., description="дата публикации (YYYY-MM-DD)")
    url: str = Field(..., description="ссылка на исследование <https://doi.org/ + ‘doi’>")
    summary: Optional[str] = Field(None, description="вывод <что исследовали/изучили/открыли> если нет — строго <None>")
    journal: str = Field(..., description="журнал")
    doi: str = Field(..., description="DOI")
    authors: Optional[str] = Field(None, description="несколько самых популярных участвующих в исследовании авторов")
    study_type: Optional[str] = Field(None, description="тип исследования (RCT/метаанализ/обзор)")
    interest: float = Field(...,
                            description="насколько исследование интересно <число с плавающей точкой, где 1.00 — максимально интересное>")


class AssistantResponseDrugResearches(BaseModel):
    researches: list[AssistantResponseDrugResearch]


class AssistantResponsePubmedQuery(BaseModel):
    """Нужна для получения оптимизированного поискового запроса для PubMed ассистенту."""
    pubmed_query: str = Field(...)
