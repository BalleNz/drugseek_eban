from enum import Enum

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime

class ActivationType(str, Enum):
    AGONIST = "agonist"
    ANTAGONIST = "antagonist"
    INVERSE_AGONIST = "inverse agonist"
    PARTIAL_AGONIST = "partial agonist"
    INHIBITOR = "inhibitor"
    ACTIVATOR = "activator"
    MODULATOR = "modulator"
    BLOCKER = "blocker"


class DosageParams(BaseModel):
    """Параметры дозировки для ответа ассистента"""
    per_time: Optional[str] = None
    max_day: Optional[str] = None
    per_time_weight_based: Optional[str] = None
    max_day_weight_based: Optional[str] = None
    notes: Optional[str] = None


class AssistantDosageDescriptionResponse(BaseModel):
    """Формализованный ответ ассистента по дозировкам и описанию"""
    drug_name: str = Field(...)
    drug_name_ru: str = Field(...)
    dosages_fun_fact: Optional[str] = None
    sources: str
    dosages: Dict[str, Dict[str, Optional[DosageParams]]]

    description: str
    classification: str

    class Config:
        allow_population_by_field_name = True


class DrugDosage(BaseModel):
    """Схема дозировки препарата из таблицы drug_dosages."""
    id: int
    drug_id: UUID
    route: str
    method: Optional[str] = None
    per_time: Optional[str] = None
    max_day: Optional[str] = None
    per_time_weight_based: Optional[str] = None
    max_day_weight_based: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DrugPathway(BaseModel):
    """Схема одной записи из таблицы drug_pathways"""
    receptor: str
    binding_affinity: Optional[str] = None
    affinity_description: str
    activation_type: ActivationType
    pathway: str
    effect: str = Field(...)

    primary_action: str
    secondary_actions: List[str] = Field(...)
    clinical_effects: List[str] = Field(...)

    sources: List[str] = Field(...)


class DrugPrice(BaseModel):
    """Схема цены препарата"""
    id: int
    drug_brandname: str
    price: float
    shop_url: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Drug(BaseModel):
    """Полная схема препарата"""
    id: UUID
    name: str
    name_ru: str
    description: str
    classification: str
    dosages_fun_fact: str
    created_at: datetime
    updated_at: datetime
    dosages: List[DrugDosage] = []
    pathways: List[DrugPathway] = []
    drug_prices: List[DrugPrice] = []

    pathways_sources: List[str] = Field(...)
    dosages_sources: List[str] = Field(...)

    @property
    def dosages_view(self) -> Dict[str, Dict[str, DosageParams]]:
        """Группировка дозировок для API"""
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
    receptor: str
    binding_affinity: Optional[str] = None
    affinity_description: str
    activation_type: ActivationType
    pathway: str
    effect: str = Field(...)

    class Config:
        from_attributes = True


class MechanismSummary(BaseModel):
    primary_action: str
    secondary_actions: List[str] = Field(...)
    clinical_effects: List[str] = Field(...)


class AssistantResponseDrugPathway(BaseModel):
    pathways: List[Pathway]
    mechanism_summary: MechanismSummary
    sources: List[str] = Field(...)

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
