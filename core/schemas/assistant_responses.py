from enum import Enum
from typing import Optional, Dict

from pydantic import BaseModel, Field

from schemas.drug_schemas import DrugAnalogSchema, Pharmacokinetics, DrugCombinationSchema, Pathway, MechanismSummary


class STATUS(Enum):
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
    status: STATUS = Field(...)
    drug_name: str = Field(default=None)


class AssistantDosageDescriptionResponse(BaseModel):
    """Формализованный ответ ассистента по дозировкам и описанию"""
    drug_name: str = Field(..., description="одно возможное название для ДВ на ENG")
    latin_name: str = Field(...)
    drug_name_ru: str = Field(...)

    synonyms: Optional[list[str]] = Field(None, description="все возможные названия для препарата на RU")

    analogs: Optional[list[DrugAnalogSchema]] = Field(None, description="аналоги препарата")
    dosages_fun_fact: Optional[str] = Field(default=None)
    description: str = Field(...)
    classification: str = Field(...)
    sources: list[str] = Field(...)

    pharmacokinetics: Pharmacokinetics

    dosages: Dict[str, Optional[Dict[str, Optional[DosageParams]]]]

    class Config:
        allow_population_by_field_name = True


class AssistantResponseCombinations(BaseModel):
    combinations: list[DrugCombinationSchema]


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
