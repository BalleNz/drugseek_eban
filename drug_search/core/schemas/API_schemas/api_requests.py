import json
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AddTokensRequest(BaseModel):
    tokens_amount: int = Field(..., description="Количество токенов")


class UserTelegramDataSchema(BaseModel):
    telegram_id: str = Field(..., description="Телеграм айди")  # telegram id
    username: str = Field(..., description="Имя пользователя (логин) для идентификации.")
    first_name: Optional[str] = Field(None, description="first name")
    last_name: Optional[str] = Field(None, description="last name")
    auth_date: Optional[datetime] = Field(datetime.now(), description="дата авторизации")

    class Config:
        from_attributes = True


class UserRequestLogSchema(BaseModel):
    user_id: uuid.UUID = Field(..., description="User ID")
    user_query: str = Field(..., description="запрос пользователя")
    used_at: datetime = Field(..., description="дата и время использования")


class QueryRequest(BaseModel):
    query: str
