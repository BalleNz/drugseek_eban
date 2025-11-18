from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from drug_search.core.lexicon.enums import SUBSCRIPTION_TYPES


class AllowedDrugSchema(BaseModel):
    drug_id: UUID = Field(..., description="ID препарата")

    class Config:
        from_attributes = True


class UserSchema(BaseModel):
    id: UUID = Field(...)
    telegram_id: str = Field(..., description="Телеграм айди")  # telegram id
    username: str = Field(..., description="Имя пользователя (логин) для идентификации.")
    first_name: Optional[str] = Field(None, description="first name")
    last_name: Optional[str] = Field(None, description="last name")

    allowed_tokens: int = Field(..., description="токены")

    used_tokens: int = Field(..., description="использованные токены")

    additional_tokens: int = Field(..., description="дополнительные токены (не сбрасываются)")

    tokens_last_refresh: datetime = Field(..., description="последний дневной сброс токенов")

    description: Optional[str] = Field(None, description="описание пользователя")
    allowed_drugs: list[AllowedDrugSchema] = Field(
        default_factory=list,
        description="Список разрешенных препаратов"
    )

    subscription_type: SUBSCRIPTION_TYPES = Field(..., description="Тип подписки юзера")
    subscription_end: Optional[datetime] = Field(None, description="когда конец подписки")

    created_at: datetime = Field(..., description="когда создан юзер")
    updated_at: Optional[datetime] = Field(None, description="когда посл обн столбца у юзера")

    def allowed_drug_ids(self):
        return [allowed_drug.drug_id for allowed_drug in self.allowed_drugs]

    class Config:
        from_attributes = True
