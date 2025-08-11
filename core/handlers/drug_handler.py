from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Path

from assistant import assistant
from schemas import UserSchema, DrugExistingResponse
from schemas.API_schemas.assistant_responses import AssistantResponseDrugValidation
from schemas.API_schemas.drug_schemas import DrugSchema
from services.drug_service import DrugService, get_drug_service
from services.user_service import UserService, get_user_service
from utils.auth import get_auth_user

drug_router = APIRouter(prefix="/drugs")


@drug_router.post("/{user_query}", description="Поиск препарата среди существующих")
async def get_exist_drug(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        user_query: str = Path(),
        drug_service: DrugService = Depends(get_drug_service),
        user_service: UserService = Depends(get_user_service)
):
    """
    Проверяет наличие препарата и его доступ у пользователя.

    :returns: {"drug_allowed": bool, "is_drug": bool, "drug": DrugSchema}
    """
    if not user.allowed_requests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User hasn't allowed requests")

    drug: DrugSchema = await drug_service.find_drug_by_query(
        user_query=user_query
    )

    is_drug = bool(drug)
    if not is_drug:
        assistant_response: AssistantResponseDrugValidation = assistant.get_user_query_validation(user_query=user_query)
        if assistant_response.status == "exist":
            # Запись нового препарата
            drug = await drug_service.new_drug(assistant_response.drug_name)
            is_drug = True
        else:
            is_drug = False

    is_allowed = drug.id in user.allowed_drugs

    return DrugExistingResponse(
        drug_exist=is_drug,
        is_allowed=is_allowed,
        drug=drug
    )


@drug_router.post(path="/allow/{drug_id}", description="Разрешает и возвращает препарат")
async def allow_drug(
        drug_service: Annotated[DrugService, Depends(get_drug_service)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        user: Annotated[UserSchema, Depends(get_auth_user)],
        drug_id: UUID = Path(..., description="ID препарата в формате UUID")
):
    """
    Разрешает препарат, который существует в БД

    Формат:
        {
            "drug": DrugSchema,
            "is_allowed": bool
        }
    """
    drug: DrugSchema = await drug_service.repo.get(drug_id)
    if drug_id in user.allowed_drugs:
        return {
            "drug": drug,
            "is_allowed": True
        }

    if not user.allowed_requests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="У юзера нет доступных запросов.")

    try:
        await user_service.reduce_tokens(user_id=user.id, tokens_to_reduce=1)
        await user_service.allow_drug_to_user(user_id=user.id, drug_id=drug_id)
        return {
            "drug": drug,
            "is_allowed": True
        }
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ex)


@drug_router.post(path="/update/{drug_id}")
async def update_existing_drug(
        user: Annotated[UserSchema, Depends(get_auth_user)]
):
    ...


@drug_router.post(path="/update/researchs/{drug_id}", description="Обновляет исследования для препарата")
async def update_drug_researchs(
        user: Annotated[UserSchema, Depends(get_auth_user)]
):
    ...
