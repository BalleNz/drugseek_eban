from typing import Union, Optional, Any, Coroutine
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Path, Body

from assistant import assistant
from database.models.user import User
from schemas import AssistantResponseDrugValidation, DrugSchema
from schemas.assistant_responses import AssistantResponseDrugValidation, STATUS
from schemas.drug_schemas import DrugSchema
from schemas.api_responses import DrugResponse
from services.drug_service import DrugService, get_drug_service
from services.user_service import UserService, get_user_service
from utils.exceptions import AssistantResponseError

drug_router = APIRouter(prefix="/drugs", tags=["Drugs"])


@drug_router.post(path="/", response_model=DrugSchema)
async def new_drug(
        user_query: Body(),
        user: User = ...,
        drug_service: DrugService = Depends(get_drug_service),
        user_service: UserService = Depends(get_user_service)
) -> AssistantResponseDrugValidation | DrugSchema:
    # TODO в одну транзакцию получать два репо а потом сервисы

    # TODO:
    # 1. Neuro_response: {"status": "exist/not exist", "drug_name":"..."}
    # 2. Отнять токен (если валидный статус)
    # 3. Create drug
    # 3. Allow drug
    # 4. Return drug
    assistant_response: AssistantResponseDrugValidation = assistant.get_user_query_validation(user_query=user_query)
    if assistant_response.status == STATUS.NOT_EXIST:
        return assistant_response
    elif assistant_response.status == STATUS.EXIST:
        if user.allowed_requests:
            drug: DrugSchema = await drug_service.new_drug(assistant_response.drug_name)
            await user_service.reduce_token(user)
            await user_service.allow_drug_to_user(user=user, drug_id=...)
            return drug

    raise AssistantResponseError


@drug_router.get("/{user_query}")
async def search_and_allow_request(
        user_query: Path(),
        user: User = ...,  # TODO: auth with O2auth schema via telegram
        drug_service: DrugService = Depends(get_drug_service)
):
    """ПОИСК ПО ТРИГРАММАМ"""
    # TODO:
    # 1. Если найден ->
    # 2. Отнять токен
    # 3. Разрешить препарат
    # 4. Вернуть препарат

    drug: DrugSchema = await drug_service.find_drug_by_query(
        user=user,
        user_query=user_query
    )

    if not drug:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drug not found")

    is_allowed = drug.id in user.allowed_drugs

    return DrugResponse(
        drug=drug,
        is_allowed=is_allowed,
    )

@drug_router.post(path="/{drug_id}")
async def update_existing_drug(

):
    ...
