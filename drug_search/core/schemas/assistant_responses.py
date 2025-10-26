from datetime import date
from typing import Optional, Dict

from pydantic import BaseModel, Field

from drug_search.core.schemas.drug_schemas import DrugAnalogSchema, Pathway, MechanismSummary, \
    CombinationType
from drug_search.core.lexicon.enums import EXIST_STATUS, DANGER_CLASSIFICATION


class DosageParams(BaseModel):
    """Параметры дозировки для ответа ассистента"""
    per_time: Optional[str] = Field(default=None)
    max_day: Optional[str] = Field(default=None)
    per_time_weight_based: Optional[str] = Field(default=None)
    max_day_weight_based: Optional[str] = Field(default=None)
    notes: str = Field(default=None)


class AssistantResponseDrugValidation(BaseModel):
    status: EXIST_STATUS = Field(...)
    drug_name: str = Field(default=None)
    drug_name_ru: str = Field(default=None, description="Название препарата на русском")
    danger_classification: Optional[DANGER_CLASSIFICATION] = Field(default=None)


class AssistantDosageDescriptionResponse(BaseModel):
    """Ответ ИИ по дозировкам и описанию препарата"""
    drug_name: str = Field(..., description="одно возможное название для ДВ на англ.")
    latin_name: str = Field(...)
    drug_name_ru: str = Field(...)
    danger_classification: DANGER_CLASSIFICATION = Field(...)

    synonyms: Optional[list[str]] = Field(None, description="все возможные названия для препарата на RU")

    analogs: Optional[list[DrugAnalogSchema]] = Field(None, description="аналоги препарата")
    dosages_fun_fact: Optional[str] = Field(default=None)
    fun_fact: Optional[str] = Field(default=None)
    description: str = Field(...)
    analogs_description: Optional[str] = Field(None, description="эффективны ли аналоги")
    metabolism_description: Optional[str] = Field(default=None)
    classification: str = Field(...)
    dosage_sources: list[str] = Field(...)

    absorption: Optional[str] = Field(default=None, description="процент биодоступности")
    metabolism: Optional[str] = Field(default=None, description="основные пути метаболизма")
    elimination: Optional[str] = Field(default=None, description="ТОП 3 (примерно) путей выведения...")
    time_to_peak: Optional[str] = Field(default=None, description="время до достижения Cmax")

    dosages: Dict[str, Optional[Dict[str, Optional[DosageParams]]]]

    class Config:
        validate_by_name = True


class AssistantResponseDrugCombination(BaseModel):
    combination_type: CombinationType
    substance: str = Field(..., description="ДВ")
    effect: str
    products: Optional[list[str]] = Field(default=None)  # only for good
    risks: Optional[str] = Field(default=None)  # only for bad


class AssistantResponseCombinations(BaseModel):
    combinations: list[AssistantResponseDrugCombination] | None


class AssistantResponseDrugPathways(BaseModel):
    pathways: list[Pathway]
    mechanism_summary: MechanismSummary
    pathway_sources: list[str] = Field(..., description="источники по путям активации")

    class Config:
        use_enum_values = True


class AssistantResponseDrugResearch(BaseModel):
    name: str = Field(..., description="название исследования")
    description: str = Field(..., description="описание исследования")
    publication_date: date = Field(..., description="дата публикации (YYYY-MM-DD)")
    url: str = Field(..., description="ссылка на исследование <https://doi.org/ + ‘doi’>")
    summary: Optional[str] = Field(None, description="вывод <что исследовали/изучили/открыли>")
    journal: str = Field(..., description="журнал")
    doi: str = Field(..., description="DOI")
    authors: Optional[str] = Field(None, description="несколько самых популярных участвующих в исследовании авторов")
    study_type: Optional[str] = Field(None, description="тип исследования (RCT/метаанализ/обзор)")
    interest: float = Field(...,
                            description="насколько исследование интересно <число с плавающей точкой, где 1.00 — "
                                        "максимально интересное>")


class AssistantResponseDrugResearches(BaseModel):
    researches: list[AssistantResponseDrugResearch]


class AssistantResponsePubmedQuery(BaseModel):
    """Нужна для получения оптимизированного поискового запроса для PubMed ассистенту."""
    pubmed_query: str = Field(...)


class AssistantResponseUserDescription(BaseModel):
    user_description: str = Field(...)
