from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from drug_search.core.lexicon.enums import ACTIONS_FROM_ASSISTANT, DANGER_CLASSIFICATION, JobStatuses
from drug_search.core.schemas.drug_schemas import DrugSchema
from drug_search.core.schemas.telegram_schemas import DrugBrieflySchema


# [ Enums, types ]
class UpdateDrugStatuses(str, Enum):
    DRUG_UPDATING = "updating"
    NOT_ENOUGH_TOKENS = "no_tokens"
    NEED_PREMIUM = "need_premium"


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


# [ Responses ]
class DrugExistingResponse(BaseModel):
    is_exist: bool | None
    danger_classification: DANGER_CLASSIFICATION | None = Field(None, description="Класс опасности")
    drug_name_ru: str | None  # если существует
    drug_name: str | None

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
    job_status: JobStatuses | None = None
    drug_name: str | None = None


class UpdateDrugResponse(BaseModel):
    status: UpdateDrugStatuses


class AllowedDrugsInfoSchema(BaseModel):
    drugs_count: int = Field(..., description="количество препаратов в базе данных")
    allowed_drugs_count: int = Field(..., description="количество разрешенных препаратов")
    allowed_drugs: Optional[list[DrugBrieflySchema]] = Field(None, description="о препарате кратко")
