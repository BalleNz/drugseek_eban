from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Path

from drug_search.core.schemas import UserSchema, DrugExistingResponse, EXIST_STATUS
from drug_search.core.schemas.assistant_responses import AssistantResponseDrugValidation
from drug_search.core.schemas.drug_schemas import DrugSchema
from drug_search.core.services.drug_service import DrugService, get_drug_service
from drug_search.core.services.user_service import UserService, get_user_service
from drug_search.core.utils.auth import get_auth_user
from drug_search.neuro_assistant.assistant import assistant

drug_router = APIRouter(prefix="/drugs")


@drug_router.post(
    "/search/{user_query}",
    description="Поиск препарата среди существующих. Создает новый препарат (после валидации), если его не было.",
    response_model=DrugExistingResponse
)
async def new_drug(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        user_query: str = Path(),
        drug_service: DrugService = Depends(get_drug_service)
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
        assistant_response: AssistantResponseDrugValidation = assistant.get_user_query_validation(user_query=user_query)
        if assistant_response.status == EXIST_STATUS.EXIST:
            # Запись нового препарата
            # TODO: rabbitmq, Celery to workflow
            await drug_service.new_drug(assistant_response.drug_name)
            # Когда создастся -> отправить сообщение в боте юзеру через воркфлоу с инлайн клавиатурой: (купить/отменить)
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
    description="Разрешает и возвращает существующий препарат"
)
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
    if not user.allowed_requests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="У юзера нет доступных запросов.")

    drug: DrugSchema | None = await drug_service.repo.get(drug_id)
    if drug_id in user.allowed_drug_ids():
        return {
            "drug": drug,
            "is_allowed": True
        }

    try:
        await user_service.reduce_tokens(user_id=user.id, tokens_to_reduce=1)
        await user_service.allow_drug_to_user(user_id=user.id, drug_id=drug_id)

        # Возможное обновление описание пользователя
        if not (user.used_requests + 1) % 10:
            await user_service.update_user_description(user_id=user.id)

        return {
            "drug": drug,
            "is_allowed": True
        }

    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ex)


@drug_router.get(path="/{drug_id}", response_model=DrugSchema)
async def get_drug(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        drug_service: Annotated[DrugService, Depends(get_drug_service)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        drug_id: UUID = Path(..., description="ID препарата в формате UUID")
):
    """Возвращает препарат по его ID"""
    if not user.allowed_requests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="У юзера нет доступных запросов.")

    drug: DrugSchema | None = await drug_service.repo.get_with_all_relationships(drug_id)

    return {
        "drug": drug,
        "is_allowed": True if drug_id in user.allowed_drug_ids() else False
    }


@drug_router.post(path="/update/researchs/{drug_id}", description="Обновляет исследования для препарата")
async def update_drug_researchs(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        drug_service: Annotated[DrugService, Depends(get_drug_service)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        drug_id: UUID = Path(..., description="ID препарата в формате UUID")
):
    """Обновляет таблицу с исследованиями препарата. Возвращает схему препарата."""
    if not user.allowed_requests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="У юзера нет доступных запросов.")

    await user_service.reduce_tokens(user.id, 1)
    await drug_service.update_drug_researchs(drug_id)

    return await drug_service.repo.get_drug(drug_id)
