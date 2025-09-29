from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from drug_search.core.dependencies.assistant_service_dep import get_assistant_service
from drug_search.core.services.assistant_service import AssistantService
from drug_search.core.schemas import QueryRequest, SelectActionResponse

assistant_router = APIRouter(prefix="/assistant")


@assistant_router.post(path="/action", response_model=SelectActionResponse)
async def action_from_assistant(
        request: QueryRequest,
        assistant_service: Annotated[AssistantService, Depends(get_assistant_service)]
):
    """Возвращает ответ с предугадыванием действия юзера"""
    return await assistant_service.predict_user_action(request.query)
