import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Path

from drug_search.core.dependencies.user_service_dep import get_user_service
from drug_search.core.dependencies.assistant_service_dep import get_assistant_service
from drug_search.core.dependencies.drug_service_dep import get_drug_service_with_deps, get_drug_service
from drug_search.core.dependencies.task_service_dep import get_task_service
from drug_search.core.schemas import (UserSchema, DrugExistingResponse,
                                      EXIST_STATUS, AssistantResponseDrugValidation, DrugSchema)
from drug_search.core.services.assistant_service import AssistantService
from drug_search.core.services.drug_service import DrugService
from drug_search.core.utils.auth import get_auth_user
from drug_search.core.services.task_service import TaskService
from drug_search.core.services.user_service import UserService

logger = logging.getLogger(__name__)
drug_router = APIRouter(prefix="/drugs")


@drug_router.post(
    "/search/{user_query}",
    description="Поиск препарата среди существующих. Создает новый препарат (после валидации), если его не было.",
    response_model=DrugExistingResponse
)
async def new_drug(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        drug_service: Annotated[DrugService, Depends(get_drug_service_with_deps)],
        assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
        task_service: Annotated[TaskService, Depends(get_task_service)],
        user_query: str = Path(),
):
    """
    Проверяет наличие препарата и его доступ у пользователя.
    Если препарата нет в БД — создает.
    :returns:
        {
            "drug_allowed": bool,
            "is_drug": bool,
            "drug": DrugSchema
        }
    """
    if not user.allowed_requests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User hasn't allowed requests")

    drug: DrugSchema | None = await drug_service.find_drug_by_query(
        user_query=user_query
    )
    drug_exist = bool(drug)

    if not drug_exist:
        assistant_response: AssistantResponseDrugValidation = await assistant_service.get_user_query_validation(
            user_query=user_query
        )
        if assistant_response.status == EXIST_STATUS.EXIST:
            # пытаемся найти по ДВ
            drug: DrugSchema | None = await drug_service.find_drug_by_query(
                user_query=assistant_response.drug_name
            )

            if not drug:
                await task_service.enqueue_drug_creation(
                    drug_name=assistant_response.drug_name,
                    user_telegram_id=user.telegram_id
                )

                return DrugExistingResponse(
                    drug_exist=True,
                    is_allowed=False,
                    drug=None
                )
        else:
            drug_exist = False

    is_allowed = False
    if drug:
        is_allowed = drug.id in user.allowed_drug_ids()

    return DrugExistingResponse(
        drug_exist=drug_exist,
        is_allowed=is_allowed,
        drug=drug
    )


@drug_router.post(
    path="/allow/{drug_id}",
    description="Разрешает и возвращает существующий препарат",
    response_model=DrugExistingResponse
)
async def allow_drug(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        drug_service: Annotated[DrugService, Depends(get_drug_service)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        drug_id: UUID = Path(..., description="ID препарата в формате UUID"),
):
    """
    Разрешает препарат, который существует в БД

    Формат:
        {
            "drug": DrugSchema,
            "is_allowed": bool
        }
    """
    if not user.allowed_requests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="У юзера нет доступных запросов.")

    drug: DrugSchema | None = await drug_service.repo.get(drug_id)
    if drug_id in user.allowed_drug_ids():
        return DrugExistingResponse(
            drug=drug,
            is_allowed=True,
            drug_exist=True
        )

    try:
        await user_service.reduce_tokens(user_id=user.id, tokens_to_reduce=1)
        await user_service.allow_drug_to_user(user_id=user.id, drug_id=drug_id)

        return DrugExistingResponse(
            drug=drug,
            is_allowed=True,
            drug_exist=True
        )

    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ex)


@drug_router.post(path="/update/{drug_id}")
async def update_old_drug(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        drug_service: Annotated[DrugService, Depends(get_drug_service)],
        drug_id: UUID = Path(..., description="ID препарата в формате UUID")
):
    """Обновляет препарат"""
    if user.allowed_requests:
        drug: DrugSchema = await drug_service.update_drug(drug_id=drug_id)
        return drug
    return {"status": "User hasn't allowed requests"}


@drug_router.get(path="/{drug_id}", response_model=DrugSchema)
async def get_drug(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        drug_service: Annotated[DrugService, Depends(get_drug_service)],
        drug_id: UUID = Path(..., description="ID препарата в формате UUID")
):
    """Возвращает препарат по его ID"""
    if not user.allowed_requests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="У юзера нет доступных запросов.")

    drug: DrugSchema | None = await drug_service.repo.get_with_all_relationships(drug_id)
    return drug


@drug_router.post(path="/update/{drug_id}/researches", description="Обновляет исследования для препарата")
async def update_drug_researches(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        drug_service: Annotated[DrugService, Depends(get_drug_service_with_deps)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        drug_id: UUID = Path(..., description="ID препарата в формате UUID")
):
    """Обновляет таблицу с исследованиями препарата. Возвращает схему препарата."""
    # TODO задачу в arq
    if not user.allowed_requests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="У юзера нет доступных запросов.")

    await user_service.reduce_tokens(user.id, 1)
    await drug_service.update_drug_researches(drug_id)

    return await drug_service.repo.get(drug_id)
