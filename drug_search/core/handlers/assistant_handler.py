from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from drug_search.core.dependencies.assistant_service_dep import get_assistant_service
from drug_search.core.dependencies.task_service_dep import get_task_service
from drug_search.core.schemas import QueryRequest, SelectActionResponse, QuestionRequest
from drug_search.core.services.assistant_service import AssistantService
from drug_search.core.services.task_service import TaskService

assistant_router = APIRouter(prefix="/assistant")


@assistant_router.post(path="/actions/predict_action", response_model=SelectActionResponse)
async def get_action(
        request: QueryRequest,
        assistant_service: Annotated[AssistantService, Depends(get_assistant_service)]
):
    """
    Возвращает ответ с предугадыванием действия юзера.
    """
    return await assistant_service.actions.predict_user_action(request.query)


@assistant_router.post(path="/actions/question")
async def question_answer(
        request: QuestionRequest,
        task_service: Annotated[TaskService, Depends(get_task_service)],
):
    """Отвечает на вопрос юзера, дает список препаратов для достижения целей"""
    await task_service.enqueue_assistant_answer(
        user_telegram_id=request.user_telegram_id,
        question=request.question,
        old_message_id=request.old_message_id,
        arrow=request.arrow
    )


# если препарат в боте не найден по drug_get (поиск по drug_name из ассистента) в АПИ
# —> дергаем ручку assistant/actions/drug_validation
# после этого спрашиваем добавить препарат или нет
