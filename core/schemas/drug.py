from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime


class DosageParams(BaseModel):
    """Параметры дозировки для ответа ассистента"""
    per_time: Optional[str] = None
    max_day: Optional[str] = None
    per_time_weight_based: Optional[str] = None
    max_day_weight_based: Optional[str] = None
    notes: Optional[str] = None


class AssistantDosageResponse(BaseModel):
    """Формализованный ответ ассистента по дозировкам"""
    drug_name: str = Field(..., alias="drug_name")
    dosages_fun_fact: Optional[str] = None
    sources: List[str]
    dosages: Dict[str, Dict[str, DosageParams]]

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
    description: str
    classification: str
    dosages_fun_fact: str
    created_at: datetime
    updated_at: datetime
    dosages: List[DrugDosage] = []
    drug_prices: List[DrugPrice] = []

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