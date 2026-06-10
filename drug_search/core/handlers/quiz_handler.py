from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from drug_search.core.dependencies.drug_service_dep import get_drug_service
from drug_search.core.dependencies.quiz_service_dep import get_quiz_service
from drug_search.core.dependencies.user_service_dep import get_user_service
from drug_search.core.schemas import UserSchema
from drug_search.core.schemas.quiz_schemas import QuizAnswerRequest, QuizAnswerResponse, QuizQuestionResponse
from drug_search.core.services.models_service.quiz_service import QuizService
from drug_search.core.services.models_service.user_service import UserService
from drug_search.core.utils.auth import get_auth_user

quiz_router = APIRouter(prefix="/quiz")


@quiz_router.get(
    "/question",
    response_model=QuizQuestionResponse,
    description="Сгенерировать вопрос викторины «Получение знаний»",
)
async def get_quiz_question(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        quiz_service: Annotated[QuizService, Depends(get_quiz_service)],
        user_service: Annotated[UserService, Depends(get_user_service)],
):
    if user.allowed_tokens + user.additional_tokens < 1:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Недостаточно токенов")

    try:
        question = await quiz_service.generate_question(user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    await user_service.reduce_tokens(user.id, tokens_amount=1)
    return question


@quiz_router.post(
    "/answer",
    response_model=QuizAnswerResponse,
    description="Проверить ответ викторины",
)
async def check_quiz_answer(
        request: QuizAnswerRequest,
        user: Annotated[UserSchema, Depends(get_auth_user)],
        quiz_service: Annotated[QuizService, Depends(get_quiz_service)],
):
    try:
        return await quiz_service.check_answer(
            quiz_id=request.quiz_id,
            selected_drug_id=request.selected_drug_id,
            user=user,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
