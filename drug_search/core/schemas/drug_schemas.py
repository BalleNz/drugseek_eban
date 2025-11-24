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
    """объект из таблицы drug_synonyms"""
    synonym: str

    class Config:
        from_attributes = True


class DrugAnalogSchema(BaseModel):
    """объект из таблицы drug_analogs"""
    analog_name: str = Field(...)
    percent: str = Field(...)
    difference: str = Field(...)

    class Config:
        from_attributes = True


class DrugCombinationSchema(BaseModel):
    """объект из таблицы drug_combinations"""
    combination_type: CombinationType = Field(...)
    substance: str = Field(..., description="ДВ или классификация")
    effect: str = Field(..., description="Эффект комбинации")
    products: list[str] | None = Field(None, description="Торговые названия (только для good)")
    risks: str | None = Field(None, description="Риски (только для bad)")

    class Config:
        from_attributes = True


class DrugDosageSchema(BaseModel):
    """объект из таблицы drug_dosages"""
    route: str = Field(...)
    method: Optional[str] = Field(default=None, description="например, внутримышечно")

    per_time: Optional[str] = Field(default=None)
    max_day: Optional[str] = Field(default=None)
    per_time_weight_based: Optional[str] = Field(default=None)
    max_day_weight_based: Optional[str] = Field(default=None)

    notes: Optional[str] = Field(default=None)

    class Config:
        from_attributes = True


class DrugPathwaySchema(BaseModel):
    """объект из таблицы drug_pathways"""
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
    drug_brand: str = Field(...)
    price: float = Field(...)
    shop_url: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    class Config:
        from_attributes = True


class ResearchType(str, Enum):
    DOSAGES = 'dosages'
    METABOLISM = 'metabolism'
    MECHANISM = 'mechanism'
    OTHER = 'other'


class DrugResearchSchema(BaseModel):
    """объект из таблицы drug_researches"""
    name: str = Field(..., description="Название исследования")
    description: str = Field(..., description="Описание исследования")
    publication_date: str = Field(..., description="Дата публикации")
    url: str = Field(..., description="Ссылка на исследование")
    summary: Optional[str] = Field(None, description="Основной вывод")
    journal: str = Field(..., description="Название журнала")
    doi: str = Field(..., description="DOI статьи")
    authors: Optional[str] = Field(None, description="Авторы")
    study_type: Optional[str] = Field(None, description="Тип исследования")
    interest: float = Field(..., description="Оценка интереса 0.00-1.00")
    research_type: ResearchType = Field(...)

    class Config:
        from_attributes = True

    @property
    def publication_date_obj(self) -> Optional[date]:
        """Преобразует строку в объект date"""
        if not self.publication_date:
            return None

        try:
            return datetime.strptime(self.publication_date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None


class Pharmacokinetics(BaseModel):
    """Информация об абсорбции для конкретного пути введения"""
    route: str = Field(..., description="Способ введения")
    bioavailability: str = Field(..., description="Биодоступность (только число процент)")
    time_to_peak: str = Field(..., description="Время до Cmax")
    onset: Optional[str] = Field(None, description="время начала действия (например, 'немедленно')")
    half_life: Optional[str] = Field(None, description="период полувыведения")
    duration: Optional[str] = Field(None, description="продолжительность действия")

    class Config:
        from_attributes = True


class EliminationInfo(BaseModel):
    """Информация о выведении через конкретный тип экскрементов"""
    excrement_type: str = Field(..., description="Тип экскремента")
    output_percent: str = Field(..., description="Процент выведения")

    class Config:
        from_attributes = True


class MetabolismPhase(BaseModel):
    """Информация о фазе метаболизма"""
    phase: str = Field(..., description="Номер фазы")
    process: str = Field(..., description="Название процесса")
    result: str = Field(..., description="Результат этого процесса")

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
    fun_facts: list[str] = Field(...)

    synonyms: list[DrugSynonymSchema] = Field(...)

    danger_classification: DANGER_CLASSIFICATION = Field(..., description="класс опасности 0/1/2")

    # [ metabolism ]
    metabolism: list[MetabolismPhase] = Field(..., description="фазы метаболизма")
    pharmacokinetics: list[Pharmacokinetics] = Field(..., description="информация о абсорбции по путям введения")
    elimination: list[EliminationInfo] = Field(..., description="пути выведения")

    metabolism_description: str = Field(...)

    # [ dosages ]
    dosages: list[DrugDosageSchema] = Field(...)
    dosage_sources: list[str] = Field(...)

    # [ pathways ]
    pathways: list[DrugPathwaySchema] = Field(...)
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
