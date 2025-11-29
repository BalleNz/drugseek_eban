from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from drug_search.core.dependencies.assistant_service_dep import get_assistant_service
from drug_search.core.dependencies.task_service_dep import get_task_service
from drug_search.core.dependencies.user_service_dep import get_user_service
from drug_search.core.schemas import QueryRequest, SelectActionResponse, QuestionDrugsRequest, QuestionRequest, \
    UserSchema
from drug_search.core.services.assistant_service import AssistantService
from drug_search.core.services.models_service.user_service import UserService
from drug_search.core.services.tasks_logic.task_service import TaskService
from drug_search.core.utils.auth import get_auth_user

assistant_router = APIRouter(prefix="/assistant")


@assistant_router.post(path="/actions/predict_action", response_model=SelectActionResponse)
async def get_action(
        request: QueryRequest,
        user: Annotated[UserSchema, Depends(get_auth_user)],
        assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
        user_service: Annotated[UserService, Depends(get_user_service)]
):
    """
    Возвращает ответ с предугадыванием действия юзера.
    """
    await user_service.repo.add_user_log_request(user.id, request.query)
    return await assistant_service.actions.predict_user_action(request.query)


@assistant_router.post(path="/actions/drugs_question")
async def drugs_question_answer(
        request: QuestionDrugsRequest,
        task_service: Annotated[TaskService, Depends(get_task_service)],
):
    """Отвечает на вопрос юзера, дает список препаратов для достижения целей"""
    await task_service.enqueue_assistant_drugs_question(
        user_telegram_id=request.user_telegram_id,
        question=request.question,
        old_message_id=request.old_message_id,
        arrow=request.arrow
    )


@assistant_router.post(path="/actions/question")
async def question_answer(
        request: QuestionRequest,
        task_service: Annotated[TaskService, Depends(get_task_service)],
):
    """Отвечает на вопрос юзера в красивом формате HTML"""
    await task_service.enqueue_assistant_question(
        user_telegram_id=request.user_telegram_id,
        question=request.question,
        old_message_id=request.old_message_id,
    )
