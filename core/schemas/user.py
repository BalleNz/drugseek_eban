from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserAllowedDrugs(BaseModel):
    user_id: UUID = Field(...)
    drug_id: UUID = Field(...)


class UserSchema(BaseModel):
    id: UUID = Field(...)
    telegram_id: str = Field(..., description="Телеграм айди")  # telegram id
    username: str = Field(..., description="Имя пользователя (логин) для идентификации.")
    first_name: Optional[str] = Field(None, description="first name")
    last_name: Optional[str] = Field(None, description="last name")

    allowed_requests: int = Field(..., description="allowed requests on drug search")
    used_requests: int = Field(..., description="count of used requests")

    description: Optional[str] = Field(None, description="описание пользователя")
    allowed_drugs: list[UserAllowedDrugs]


class UserTelegramDataSchema(BaseModel):
    telegram_id: str = Field(..., description="Телеграм айди")  # telegram id
    username: str = Field(..., description="Имя пользователя (логин) для идентификации.")
    first_name: Optional[str] = Field(None, description="first name")
    last_name: Optional[str] = Field(None, description="last name")
    auth_date: datetime = Field(None, description="дата авторизации")

    class Config:
        from_attributes = True
