from typing import Optional

from pydantic import BaseModel

from drug_search.core.lexicon.enums import ACTIONS_FROM_ASSISTANT
from drug_search.core.schemas.drug_schemas import DrugSchema


class DrugExistingResponse(BaseModel):
    drug_exist: bool
    drug: Optional[DrugSchema]
    is_allowed: bool


class SelectActionResponse(BaseModel):
    action: ACTIONS_FROM_ASSISTANT


class DrugAnswer:
    drug_name: str
    efficiency: str
    description: str


class AnswerAssistantResponse:
    answer: str
    drugs: list[DrugAnswer]
