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
    auth_date: datetime = Field(None, description="дата авторизации")

    class Config:
        from_attributes = True
