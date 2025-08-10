from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class ActivationType(str, Enum):
    AGONIST = "agonist"
    ANTAGONIST = "antagonist"
    INVERSE_AGONIST = "inverse agonist"
    PARTIAL_AGONIST = "partial agonist"
    INHIBITOR = "inhibitor"
    ACTIVATOR = "activator"
    MODULATOR = "modulator"
    BLOCKER = "blocker"
    OTHER = "other"


class CombinationType(str, Enum):
    GOOD = 'good'
    BAD = 'bad'


class Pharmacokinetics(BaseModel):
    absorption: Optional[str] = Field(default=None, description="процент биодоступности")
    metabolism: Optional[str] = Field(default=None, description="основные пути метаболизма")
    elimination: Optional[str] = Field(default=None, description="ТОП 3 (примерно) путей выведения...")
    time_to_peak: Optional[str] = Field(default=None, description="время до достижения Cmax")


class DrugSynonymSchema(BaseModel):
    synonym: str


class DrugAnalogSchema(BaseModel):
    analog_name: str = Field(...)
    percent: float = Field(...)
    difference: str = Field(...)


class DrugCombinationSchema(BaseModel):
    id: UUID = Field(...)
    combination_type: CombinationType
    substance: str
    effect: str
    products: Optional[List[str]] = Field(default=None)  # only for good
    risks: Optional[str] = Field(default=None)  # only for bad
    sources: List[str]


class DrugDosageSchema(BaseModel):
    """Схема дозировки препарата из таблицы drug_dosages."""
    id: UUID = Field(...)
    drug_id: UUID = Field(...)

    route: str = Field(...)
    method: Optional[str] = Field(default=None)

    per_time: Optional[str] = Field(default=None)
    max_day: Optional[str] = Field(default=None)
    per_time_weight_based: Optional[str] = Field(default=None)
    max_day_weight_based: Optional[str] = Field(default=None)

    onset: str = Field(None, description="время начала действия (например, 'немедленно')")
    half_life: str = Field(None, description="период полувыведения")
    duration: str = Field(None, description="продолжительность действия")

    notes: Optional[str] = Field(default=None)

    class Config:
        from_attributes = True


class DrugPathwaySchema(BaseModel):
    """Схема одной записи из таблицы drug_pathways"""
    id: UUID = Field(...)
    receptor: str = Field(...)
    binding_affinity: Optional[str] = Field(default=None)
    affinity_description: str = Field(...)
    activation_type: ActivationType
    pathway: str = Field(...)
    effect: str = Field(...)

    source: str = Field(...)
    note: str = Field(...)


class DrugPriceSchema(BaseModel):
    """Схема цены препарата"""
    id: int = Field(...)
    drug_brandname: str = Field(...)
    price: float = Field(...)
    shop_url: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    class Config:
        from_attributes = True


class DrugResearchSchema(BaseModel):
    name: str = Field(..., description="название исследования")
    description: str = Field(..., description="описание исследования")
    publication_date: date = Field(..., description="дата публикации")
    url: str = Field(..., description="ссылка на исследование")
    summary: Optional[str] = Field(None, description="вывод исследования")
    journal: str = Field(..., description="журнал")
    doi: str = Field(..., description="DOI")
    authors: Optional[str] = Field(None, description="авторы")
    study_type: Optional[str] = Field(None, description="тип исследования")
    interest: float = Field(..., description="уровень интереса")

    class Config:
        from_attributes = True


class DrugSchema(BaseModel):
    """Полная схема препарата"""
    id: UUID = Field(...)
    name: str = Field(...)
    latin_name: Optional[str] = Field(default=None)
    name_ru: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    classification: Optional[str] = Field(default=None)
    dosages_fun_fact: Optional[str] = Field(default=None)

    synonyms: Optional[list[DrugSynonymSchema]] = Field(default_factory=list)  # в планах не подгружать лишний раз таблицу , пока будет пустая
    dosages: list[DrugDosageSchema] = Field(default_factory=list)
    pathways: list[DrugPathwaySchema] = Field(default_factory=list)
    analogs: list[DrugAnalogSchema] = Field(default_factory=list)
    combinations: list[DrugCombinationSchema] = Field(default_factory=list)
    researchs: list[DrugResearchSchema] = Field(default_factory=list)

    drug_prices: Optional[list[DrugPriceSchema]] = Field(default=None)  # FUTURE

    pathways_sources: list[str] = Field(default_factory=list)
    dosages_sources: list[str] = Field(default_factory=list)

    primary_action: str = Field(...)
    secondary_actions: str = Field(...)
    clinical_effects: str = Field(...)

    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    class Config:
        from_attributes = True


class Pathway(BaseModel):
    receptor: str = Field(...)
    binding_affinity: Optional[str] = None
    affinity_description: str = Field(...)
    activation_type: ActivationType
    pathway: str = Field(...)
    effect: str = Field(...)

    source: str = Field(...)
    note: str = Field(...)

    class Config:
        from_attributes = True


class MechanismSummary(BaseModel):
    primary_action: str = Field(...)
    secondary_actions: Optional[str] = Field(None)
    clinical_effects: str = Field(...)
    sources: list[str] = Field(...)
