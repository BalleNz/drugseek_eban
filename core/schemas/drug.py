from pydantic import BaseModel, Field
from typing import Optional, Dict


class DosageParams(BaseModel):
    per_time: Optional[str] = None
    max_day: Optional[str] = None
    per_time_weight_based: Optional[str] = None
    max_day_weight_based: Optional[str] = None
    notes: Optional[str] = None


class AssistantDosageResponse(BaseModel):
    drug_name: str = Field(..., alias="drug_name")
    dosages_fun_fact: Optional[str] = None
    sources: list[str]
    dosages: Dict[str, Dict[str, DosageParams]]

    class Config:
        allow_population_by_field_name = True
