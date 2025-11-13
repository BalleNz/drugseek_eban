import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from drug_search.core.lexicon.enums import DANGER_CLASSIFICATION, ARROW_TYPES
from drug_search.bot.lexicon.enums import DrugMenu


class AddTokensRequest(BaseModel):
    amount_search_tokens: int = Field(..., description="Токены для поиска")
    amount_question_tokens: int = Field(..., description="Токены для вопросов")


class UserTelegramDataSchema(BaseModel):
    telegram_id: str = Field(..., description="Телеграм айди")  # telegram id
    username: str = Field(..., description="Имя пользователя (логин) для идентификации.")
    first_name: Optional[str] = Field(None, description="first name")
    last_name: Optional[str] = Field(None, description="last name")
    auth_date: datetime | None = Field(datetime.now(), description="дата авторизации")

    class Config:
        from_attributes = True


class UserRequestLogSchema(BaseModel):
    user_id: uuid.UUID = Field(..., description="User ID")
    user_query: str = Field(..., description="запрос пользователя")
    used_at: datetime = Field(..., description="дата и время запроса")


class QueryRequest(BaseModel):
    query: str


# [ Question ]
class QuestionRequest(BaseModel):
    user_telegram_id: str
    question: str
    old_message_id: str
    arrow: ARROW_TYPES


class QuestionContinueRequest(BaseModel):
    user_telegram_id: str
    question: str
    old_message_id: str


# [ Actions ]
class BuyDrugRequest(BaseModel):
    drug_id: uuid.UUID | None  # если нужно создавать: None
    drug_name: str
    danger_classification: DANGER_CLASSIFICATION


# [ ADMIN ]
class MailingRequest(BaseModel):
    message: str
