from pydantic import BaseModel, Field


class AddTokensRequest(BaseModel):
    tokens_amount: int = Field(..., description="Количество токенов")
