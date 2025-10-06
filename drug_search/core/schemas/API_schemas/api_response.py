from typing import Optional

from pydantic import BaseModel, Field

from drug_search.core.lexicon.enums import ACTIONS_FROM_ASSISTANT, DANGER_CLASSIFICATION
from drug_search.core.schemas.drug_schemas import DrugSchema


class DrugExistingResponse(BaseModel):
    is_exist: bool | None
    danger_classification: DANGER_CLASSIFICATION | None = Field(None, description="Класс опасности (0/1/2)")

    is_drug_in_database: bool | None
    drug: DrugSchema | None
    is_allowed: bool | None = Field(None)


# Assistant Actions
class SelectActionResponse(BaseModel):
    action: ACTIONS_FROM_ASSISTANT


class DrugAnswer(BaseModel):
    drug_name: str
    efficiency: str
    description: str


class QuestionAssistantResponse(BaseModel):
    answer: str = Field(..., description="Ответ на вопрос пользователя")
    drugs: list[DrugAnswer] | None = Field(None, description="Препараты которые помогут в решении вопроса")
