import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Path

from arq_tasks import DrugOperations
from drug_search.core.dependencies.assistant_service_dep import get_assistant_service
from drug_search.core.dependencies.cache_bot_service_dep import get_cache_service
from drug_search.core.dependencies.drug_service_dep import get_drug_service_with_deps, get_drug_service
from drug_search.core.dependencies.task_service_dep import get_task_service
from drug_search.core.dependencies.user_service_dep import get_user_service
from drug_search.core.lexicon.enums import EXIST_STATUS
from drug_search.core.schemas import (UserSchema, DrugExistingResponse,
                                      AssistantResponseDrugValidation, DrugSchema)
from drug_search.core.services.assistant_service import AssistantService
from drug_search.core.services.cache_service import CacheService
from drug_search.core.services.drug_service import DrugService
from drug_search.core.services.task_service import TaskService
from drug_search.core.services.user_service import UserService
from drug_search.core.utils.auth import get_auth_user

logger = logging.getLogger(__name__)
drug_router = APIRouter(prefix="/drugs")


@drug_router.post(
    "/new/{drug_name}",
    description="Создает новый препарат (в ARQ), затем отсылается уведомление с клавиатурой",
)
async def new_drug(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        task_service: Annotated[TaskService, Depends(get_task_service)],
        drug_name: str = Path(description="ДВ")
):
    """Создает препарат в ARQ через TaskService"""
    if not user.allowed_search_requests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User hasn't allowed requests")

    try:
        task_response = await task_service.enqueue_drug_operations(
            operation=DrugOperations.CREATE,
            user_telegram_id=user.telegram_id,
            user_id=user.id,
            drug_name=drug_name
        )
        logger.info(f"✅ Drug creation job enqueued with ID: {task_response["job_id"]}")

        return {
            "status": task_response["status"],
            "job_id": task_response["job_id"],
            "message": task_response["message"]
        }
    except Exception as ex:
        return {"status": 0, "exception": str(ex)}


@drug_router.get(
    path="/search/{drug_name_query}",
    description="поиск препарата ассистентом; Использует триграммы",
    response_model=DrugExistingResponse
)
async def search_drug(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        drug_service: Annotated[DrugService, Depends(get_drug_service)],
        assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
        drug_name_query: str = Path(..., description="Предполагаемое название препарата"),
):
    drug: DrugSchema | None = await drug_service.find_drug_by_query(
        user_query=drug_name_query
    )
    is_drug_in_database = bool(drug)

    if is_drug_in_database:
        return DrugExistingResponse(
            is_exist=True,
            is_drug_in_database=True,
            drug=drug,
            is_allowed=drug.id in user.allowed_drug_ids(),
            danger_classification=drug.danger_classification
        )

    if not is_drug_in_database:
        """Валидирует препарат на существование, дает ему характеристику (danger_class)"""
        assistant_response: AssistantResponseDrugValidation = await assistant_service.get_user_query_validation(
            user_query=drug_name_query
        )

        if assistant_response.status == EXIST_STATUS.EXIST:

            # Еще раз пытаемся найти по ДВ в Базе
            drug: DrugSchema | None = await drug_service.find_drug_by_query(
                user_query=assistant_response.drug_name
            )

            return DrugExistingResponse(
                is_exist=True,
                is_drug_in_database=bool(drug),  # может быть найден, а может и нет
                is_allowed=drug.id in user.allowed_drug_ids() if bool(drug) else None,
                drug=drug,  # Drug | None
                danger_classification=assistant_response.danger_classification
            )

        else:  # препарат не существует в принципе
            return DrugExistingResponse(
                is_exist=False,
                is_drug_in_database=False,
                is_allowed=False,
                drug=None,
                danger_classification=assistant_response.danger_classification
            )


@drug_router.get(
    path="/search/trigrams/{drug_name_query}",
    description="триграмм-поиск препарата",
    response_model=DrugExistingResponse
)
async def search_drug_only_trigrams(
        drug_service: Annotated[DrugService, Depends(get_drug_service)],
        user: Annotated[UserSchema, Depends(get_auth_user)],
        drug_name_query: str = Path(..., description="Строго действующее вещество"),
):
    drug: DrugSchema | None = await drug_service.find_drug_by_query(drug_name_query)

    return DrugExistingResponse(
        is_exist=True if drug else None,
        is_drug_in_database=True if drug else False,
        is_allowed=drug.id in user.allowed_drug_ids() if drug else None,
        drug=drug,
        danger_classification=drug.danger_classification if drug else None,
    )


@drug_router.get(
    path="/search/without_trigrams/{drug_name_query}",
    description="поиск препарата без триграмм",
    response_model=DrugExistingResponse
)
async def search_drug_without_trigrams(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        drug_service: Annotated[DrugService, Depends(get_drug_service)],
        assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
        drug_name_query: str = Path(..., description="Строго действующее вещество"),
):
    """
    Нужен для случая если из предыдущей ручки найден не тот препарат.

    Условие:
    Препарат точно существует.

    На вход подается строго действующее вещество
    """
    validation_response: AssistantResponseDrugValidation = await assistant_service.get_user_query_validation(
        drug_name_query)
    logger.info(validation_response.model_dump_json())

    if validation_response.status == EXIST_STATUS.NOT_EXIST:
        logger.info(f"Drug {drug_name_query} not exist!\n {validation_response.model_dump_json()}")
        return DrugExistingResponse(
            is_exist=False,
            is_drug_in_database=False,
            is_allowed=False,
            drug=None,
            danger_classification=None
        )

    drug: DrugSchema | None = await drug_service.repo.find_drug_without_trigrams(validation_response.drug_name)
    return DrugExistingResponse(
        is_exist=True,
        is_drug_in_database=bool(drug),
        is_allowed=drug.id in user.allowed_drug_ids() if drug else None,
        drug=drug,
        danger_classification=validation_response.danger_classification
    )


@drug_router.post(
    path="/allow/{drug_id}",
    description="Разрешает и возвращает существующий препарат",
)
async def allow_drug(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        cache_service: Annotated[CacheService, Depends(get_cache_service)],
        drug_id: UUID = Path(..., description="ID препарата в формате UUID"),
):
    """Разрешает препарат, который существует в БД"""
    if not user.allowed_search_requests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="У юзера нет доступных запросов.")

    try:
        await user_service.reduce_tokens(user_id=user.id, tokens_to_reduce=1)
        await user_service.allow_drug_to_user(user_id=user.id, drug_id=drug_id)

        await cache_service.redis_service.invalidate_user_data(telegram_id=user.telegram_id)

        return {"status": 1}

    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ex)


@drug_router.post(path="/update/{drug_id}")
async def update_old_drug(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        drug_service: Annotated[DrugService, Depends(get_drug_service)],
        drug_id: UUID = Path(..., description="ID препарата в формате UUID")
):
    """Обновляет препарат"""
    # TODO ARQ
    ...
    if user.allowed_search_requests:
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
    if not user.allowed_search_requests:
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
    if not user.allowed_search_requests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="У юзера нет доступных запросов.")

    await user_service.reduce_tokens(user.id, 1)
    await drug_service.update_drug_researches(drug_id)

    return await drug_service.repo.get(drug_id)
