from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List
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


class DosageParams(BaseModel):
    """Параметры дозировки для ответа ассистента"""
    per_time: Optional[str] = Field(default=None)
    max_day: Optional[str] = Field(default=None)
    per_time_weight_based: Optional[str] = Field(default=None)
    max_day_weight_based: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class Pharmacokinetics(BaseModel):
    absorption: Optional[str] = Field(default=None, description="процент биодоступности")
    metabolism: Optional[str] = Field(default=None, description="основные пути метаболизма")
    excretion: Optional[str] = Field(default=None, description="ТОП 3 (примерно) путей выведения...")
    time_to_peak: Optional[str] = Field(default=None, description="время до достижения Cmax")


class DrugSynonym(BaseModel):
    synonym: str


class DrugAnalog(BaseModel):
    analog_name: str = Field(...)
    percent: float = Field(...)
    difference: str = Field(...)


class AssistantDosageDescriptionResponse(BaseModel):
    """Формализованный ответ ассистента по дозировкам и описанию"""
    drug_name: str = Field(..., description="одно возможное название для ДВ на ENG")
    latin_name: str = Field(...)
    drug_name_ru: Optional[list[str]] = Field(None, description="все возможные названия для препарата на RU")

    analogs: Optional[list[DrugAnalog]] = Field(None, description="аналоги препарата")
    dosages_fun_fact: Optional[str] = Field(default=None)
    description: str = Field(...)
    classification: str = Field(...)
    sources: list[str] = Field(...)

    pharmacokinetics: Pharmacokinetics

    dosages: Dict[str, Optional[Dict[str, Optional[DosageParams]]]]

    class Config:
        allow_population_by_field_name = True


class Combination(BaseModel):
    combination_type: CombinationType
    substance: str
    effect: str
    products: Optional[List[str]] = Field(default=None)  # only for good
    risks: Optional[str] = Field(default=None)  # only for bad
    sources: List[str]


class AssistantResponseCombinations(BaseModel):
    combinations: list[Combination]


class DrugDosage(BaseModel):
    """Схема дозировки препарата из таблицы drug_dosages."""
    id: int = Field(...)
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
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    class Config:
        from_attributes = True


class DrugPathway(BaseModel):
    """Схема одной записи из таблицы drug_pathways"""
    receptor: str = Field(...)
    binding_affinity: Optional[str] = Field(default=None)
    affinity_description: str = Field(...)
    activation_type: ActivationType
    pathway: str = Field(...)
    effect: str = Field(...)

    primary_action: str = Field(...)
    secondary_actions: List[str] = Field(...)
    clinical_effects: List[str] = Field(...)

    source: str = Field(...)
    note: str = Field(...)


class DrugPrice(BaseModel):
    """Схема цены препарата"""
    id: int = Field(...)
    drug_brandname: str = Field(...)
    price: float = Field(...)
    shop_url: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    class Config:
        from_attributes = True


class Drug(BaseModel):
    """Полная схема препарата"""
    id: UUID = Field(...)
    name: str = Field(...)
    latin_name: str = Field(default=None)
    name_ru: list[str] = Field(...)
    description: str = Field(...)
    analogs: str = Field(default=None)
    classification: str = Field(...)
    dosages_fun_fact: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    dosages: List[DrugDosage] = []
    pathways: List[DrugPathway] = []
    drug_prices: List[DrugPrice] = []

    pathways_sources: List[str] = Field(...)
    dosages_sources: List[str] = Field(...)

    @property
    def dosages_view(self) -> Dict[str, Dict[str, DosageParams]]:
        """
        Группировка дозировок для API.

        Для вида:
            - Drug.dosages_view["other"]["peroral"].max_day
        """
        result = {}
        for dosage in self.dosages:
            route_group = result.setdefault(dosage.route, {})
            route_group[dosage.method] = DosageParams(
                per_time=dosage.per_time,
                max_day=dosage.max_day,
                per_time_weight_based=dosage.per_time_weight_based,
                max_day_weight_based=dosage.max_day_weight_based,
                notes=dosage.notes
            )
        return result

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
    secondary_actions: str = Field(...)
    clinical_effects: str = Field(...)
    sources: list[str] = Field(...)


class AssistantResponseDrugPathway(BaseModel):
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
                    "activation_type": "antagonist",
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
