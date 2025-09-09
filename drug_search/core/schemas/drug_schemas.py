from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class CombinationType(str, Enum):
    GOOD = 'good'
    BAD = 'bad'


class Pharmacokinetics(BaseModel):
    absorption: Optional[str] = Field(default=None, description="процент биодоступности")
    metabolism: Optional[str] = Field(default=None, description="основные пути метаболизма")
    elimination: Optional[str] = Field(default=None, description="ТОП 3 (примерно) путей выведения...")
    time_to_peak: Optional[str] = Field(default=None, description="время до достижения Cmax")


class DrugSynonymResponse(BaseModel):
    id: UUID
    drug_id: UUID
    synonym: str

    class Config:
        from_attributes = True


class DrugAnalogSchemaRequest(BaseModel):
    analog_name: str = Field(...)
    percent: float = Field(...)
    difference: str = Field(...)

    class Config:
        from_attributes = True


class DrugAnalogResponse(BaseModel):
    id: UUID
    drug_id: UUID
    analog_name: str = Field(...)
    percent: float = Field(...)
    difference: str = Field(...)

    class Config:
        from_attributes = True


class DrugCombinationResponse(BaseModel):
    id: UUID = Field(...)
    drug_id: UUID
    combination_type: CombinationType
    substance: str
    effect: str
    products: Optional[List[str]] = Field(default=None)  # only for good
    risks: Optional[str] = Field(default=None)  # only for bad
    sources: List[str]

    class Config:
        from_attributes = True


class DrugDosageResponse(BaseModel):
    """Схема дозировки препарата из таблицы drug_dosages."""
    id: UUID = Field(...)
    drug_id: UUID = Field(...)

    route: str = Field(...)
    method: Optional[str] = Field(default=None)

    per_time: Optional[str] = Field(default=None)
    max_day: Optional[str] = Field(default=None)
    per_time_weight_based: Optional[str] = Field(default=None)
    max_day_weight_based: Optional[str] = Field(default=None)

    onset: Optional[str] = Field(None, description="время начала действия (например, 'немедленно')")
    half_life: Optional[str] = Field(None, description="период полувыведения")
    duration: Optional[str] = Field(None, description="продолжительность действия")

    notes: Optional[str] = Field(default=None)

    class Config:
        from_attributes = True


class DrugPathwayResponse(BaseModel):
    """Схема одной записи из таблицы drug_pathways"""
    id: UUID = Field(...)
    drug_id: UUID
    receptor: str = Field(...)
    binding_affinity: Optional[str] = Field(default=None)
    affinity_description: str = Field(...)
    activation_type: str = Field(...)
    pathway: str = Field(...)
    effect: str = Field(...)

    note: str = Field(...)

    class Config:
        from_attributes = True


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


class DrugResearchResponse(BaseModel):
    id: UUID
    drug_id: UUID
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

    synonyms: Optional[list[DrugSynonymResponse]] = Field(default_factory=list)  # в планах не подгружать лишний раз таблицу , пока будет пустая
    dosages: list[DrugDosageResponse] = Field(default_factory=list)
    pathways: list[DrugPathwayResponse] = Field(default_factory=list)
    analogs: list[DrugAnalogSchemaRequest] = Field(default_factory=list)
    combinations: list[DrugCombinationResponse] = Field(default_factory=list)
    researchs: list[DrugResearchResponse] = Field(default_factory=list)

    drug_prices: Optional[list[DrugPriceSchema]] = Field(default=None)  # FUTURE

    pathways_sources: Optional[list[str]] = Field(default_factory=list)  # TODO удалить
    dosages_sources: Optional[list[str]] = Field(default_factory=list)

    primary_action: Optional[str] = Field(...)
    secondary_actions: Optional[str] = Field(...)
    clinical_effects: Optional[str] = Field(...)

    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    is_danger: bool = Field(..., description="Является ли препарат запрещенным")

    class Config:
        from_attributes = True


class Pathway(BaseModel):
    receptor: str = Field(...)
    binding_affinity: Optional[str] = None
    affinity_description: str = Field(...)
    activation_type: str = Field(...)
    pathway: str = Field(...)
    effect: str = Field(...)

    note: str = Field(...)

    class Config:
        from_attributes = True


class MechanismSummary(BaseModel):
    primary_action: str = Field(...)
    secondary_actions: Optional[str] = Field(None)
    clinical_effects: str = Field(...)
    sources: list[str] = Field(...)

    class Config:
        from_attributes = True
