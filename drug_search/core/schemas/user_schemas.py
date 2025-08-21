from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


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

    allowed_requests: int = Field(..., description="allowed requests on drug search")
    used_requests: int = Field(..., description="count of used requests")

    description: Optional[str] = Field(None, description="описание пользователя")
    allowed_drugs: list[AllowedDrugSchema] = Field(
        default_factory=list,
        description="Список разрешенных препаратов"
    )

    def allowed_drug_ids(self):
        return [allowed_drug.drug_id for allowed_drug in self.allowed_drugs]

    class Config:
        from_attributes = True
