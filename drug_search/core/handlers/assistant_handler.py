from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from drug_search.core.dependencies.assistant_service_dep import get_assistant_service
from drug_search.core.services.assistant_service import AssistantService
from drug_search.core.schemas import QueryRequest, SelectActionResponse, QuestionAssistantResponse

assistant_router = APIRouter(prefix="/assistant")


@assistant_router.post(path="/actions/predict_action", response_model=SelectActionResponse)
async def get_action(
        request: QueryRequest,
        assistant_service: Annotated[AssistantService, Depends(get_assistant_service)]
):
    """Возвращает ответ с предугадыванием действия юзера"""
    return await assistant_service.actions.predict_user_action(request.query)


@assistant_router.post(path="/actions/question", response_model=QuestionAssistantResponse)
async def action_answer(
        request: QueryRequest,
        assistant_service: Annotated[AssistantService, Depends(get_assistant_service)]
):
    """Отвечает на вопрос юзера, дает список препаратов для достижения целей"""
    return await assistant_service.actions.answer_to_question(question=request.query)


# если препарат в боте не найден по drug_get (поиск по drug_name из ассистента) в АПИ
# —> дергаем ручку assistant/actions/drug_validation
# после этого спрашиваем добавить препарат или нет
