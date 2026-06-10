import uuid

from pydantic import BaseModel, Field


class QuizDrugSchema(BaseModel):
    drug_id: uuid.UUID
    drug_name: str
    drug_name_ru: str | None = None
    description: str | None = None
    classification: str | None = None
    primary_action: str | None = None
    fact: str | None = None


class QuizOptionSchema(BaseModel):
    drug_id: uuid.UUID
    name: str = Field(..., description="Отображаемое название варианта ответа")


class QuizQuestionResponse(BaseModel):
    quiz_id: str
    question: str
    options: list[QuizOptionSchema]


class QuizAnswerRequest(BaseModel):
    quiz_id: str
    selected_drug_id: uuid.UUID


class QuizAnswerResponse(BaseModel):
    is_correct: bool
    correct_name: str
    explanation: str | None = None
