import uuid
from typing import Optional

from pydantic import BaseModel, Field


class DrugBrieflySchema(BaseModel):
    drug_id: uuid.UUID
    drug_name_ru: str


class AllowedDrugsSchema(BaseModel):
    drugs_count: int = Field(..., description="количество препаратов в базе данных")
    allowed_drugs_count: int = Field(..., description="количество разрешенных препаратов")
    allowed_drugs: Optional[list[DrugBrieflySchema]] = Field(None, description="о препарате кратко")
