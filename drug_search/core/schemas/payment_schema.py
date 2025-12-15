import uuid

from pydantic import BaseModel, Field


class PaymentSchema(BaseModel):
    user_id: uuid.UUID = Field(..., description="user id")
    package_key: str = Field(..., description="ключ пакета")
    payment_name: str = Field(..., description="название платежа")
    price: int = Field(..., description="сумма в рублях")


class PaymentRequest(BaseModel):
    product_key: str = Field(..., description="ключ пакета")
    sub_days: int = Field(0, description="дни текущей подписки (до покупки)")
    user_telegram_id: str
