import uuid

from pydantic import BaseModel


class DrugBrieflySchema(BaseModel):
    drug_id: uuid.UUID
    drug_name_ru: str
