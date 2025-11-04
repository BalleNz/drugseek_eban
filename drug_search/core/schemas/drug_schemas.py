from datetime import datetime, date
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from drug_search.core.lexicon.enums import DANGER_CLASSIFICATION


class CombinationType(str, Enum):
    GOOD = 'good'
    BAD = 'bad'


class DrugSynonymSchema(BaseModel):
    synonym: str

    class Config:
        from_attributes = True


class DrugAnalogSchema(BaseModel):
    analog_name: str = Field(...)
    percent: str = Field(...)
    difference: str = Field(...)

    class Config:
        from_attributes = True


class DrugCombinationSchema(BaseModel):
    combination_type: CombinationType = Field(...)
    substance: str = Field(..., description="ДВ или классификация")
    effect: str = Field(..., description="Эффект комбинации")
    products: list[str] | None = Field(None, description="Торговые названия (только для good)")
    risks: str | None = Field(None, description="Риски (только для bad)")

    class Config:
        from_attributes = True


class DrugDosageSchema(BaseModel):
    """Схема дозировки препарата из таблицы drug_dosages."""
    route: str = Field(...)
    method: Optional[str] = Field(default=None, description="например, внутримышечно")

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


class Pathway(BaseModel):
    """Схема одной записи из таблицы drug_pathways"""
    receptor: str = Field(...)
    binding_affinity: Optional[str] = Field(default=None)
    affinity_description: str = Field(...)
    activation_type: str = Field(...)
    pathway: str = Field(...)
    effect: str = Field(...)

    note: str = Field(...)

    class Config:
        from_attributes = True


class MechanismSummary(BaseModel):
    primary_action: str = Field(...)
    secondary_actions: Optional[str] = Field(None, )
    clinical_effects: str = Field(...)

    class Config:
        from_attributes = True


class DrugPriceSchema(BaseModel):
    """Схема цены препарата"""
    # FUTURE
    id: int = Field(...)
    drug_brandname: str = Field(...)
    price: float = Field(...)
    shop_url: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    class Config:
        from_attributes = True


class DrugResearchSchema(BaseModel):
    """объект из таблицы drug_researches"""
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

    class Config:
        from_attributes = True


class DrugSchema(BaseModel):
    """Полная схема препарата"""
    id: UUID = Field(...)

    # [ briefly info ]
    name: str = Field(...)
    latin_name: str = Field(...)
    name_ru: str = Field(...)
    description: str = Field(...)
    classification: str = Field(...)
    fact: str = Field(...)
    synonyms: list[DrugSynonymSchema] = Field(...)

    danger_classification: DANGER_CLASSIFICATION = Field(..., description="класс опасности 0/1/2")

    # [ metabolism ]
    absorption: list[str] = Field(..., description="процент биодоступности")
    metabolism: list[str] = Field(..., description="основные пути метаболизма")
    elimination: str = Field(..., description="ТОП 3 (примерно) путей выведения...")
    time_to_peak: str = Field(..., description="время до достижения Cmax")
    metabolism_description: str = Field(...)

    # [ dosages ]
    dosages: list[DrugDosageSchema] = Field(...)
    dosages_fun_facts: list[str] = Field(...)
    dosage_sources: list[str] = Field(...)

    # [ pathways ]
    pathways: list[Pathway] = Field(...)
    pathways_sources: list[str] = Field(...)
    primary_action: str = Field(...)
    secondary_actions: str = Field(...)
    clinical_effects: str = Field(...)

    # [ analogs ]
    analogs: list[DrugAnalogSchema] = Field(...)
    analogs_description: str = Field(...)

    # [ combinations ]
    combinations: list[DrugCombinationSchema] = Field(...)

    # [ researches ]
    researches: list[DrugResearchSchema] = Field(...)

    prices: list[DrugPriceSchema] | None = Field(None)

    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    class Config:
        from_attributes = True
