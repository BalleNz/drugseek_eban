from enum import Enum

from pydantic import BaseModel, Field

from drug_search.core.lexicon.enums import ACTIONS_FROM_ASSISTANT, DANGER_CLASSIFICATION
from drug_search.core.schemas.drug_schemas import DrugSchema


# [ Enums, types ]
class BuyDrugStatuses(str, Enum):
    DRUG_CREATED = "created"  # and allowed
    DRUG_ALLOWED = "allowed"
    NOT_ENOUGH_TOKENS = "no_tokens"
    NEED_PREMIUM = "need_premium"
    DANGER = "danger"


class DrugAnswer(BaseModel):
    drug_name: str
    efficiency: str
    description: str


class DrugExistingResponse(BaseModel):
    is_exist: bool | None
    danger_classification: DANGER_CLASSIFICATION | None = Field(None, description="Класс опасности")
    drug_name_ru: str | None  # если существует

    # if exist in database
    is_drug_in_database: bool | None
    drug: DrugSchema | None
    is_allowed: bool | None = Field(None)


class SelectActionResponse(BaseModel):
    action: ACTIONS_FROM_ASSISTANT
    drug_name: str | None = Field(default=None, description="ДВ")
    drug_menu: str | None = Field(default=None, description="predicted Callback")


class QuestionAssistantResponse(BaseModel):
    answer: str = Field(..., description="Ответ на вопрос пользователя")
    drugs: list[DrugAnswer] | None = Field(None, description="Препараты которые помогут в решении вопроса")


class BuyDrugResponse(BaseModel):
    status: BuyDrugStatuses
    drug_name: str | None = None
