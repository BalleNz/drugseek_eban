from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from drug_search.core.dependencies.cache_service_dep import get_cache_service
from drug_search.core.dependencies.user_service_dep import get_user_service, get_user_service_with_assistant
from drug_search.core.schemas import UserSchema, AllowedDrugsSchema, AddTokensRequest
from drug_search.core.services.cache_service import CacheService
from drug_search.core.services.user_service import UserService
from drug_search.core.utils.auth import get_auth_user

user_router = APIRouter(prefix="/user")


@user_router.get(
    path="/",
    response_model=UserSchema,
    description="Получить описание юзера"
)
async def get_user(
        user: Annotated[UserSchema, Depends(get_auth_user)],
):
    return user


@user_router.get(
    path="/allowed",
    description="Получение всех разрешенных препаратов, а также общее количество препаратов в базе.",
    response_model=AllowedDrugsSchema
)
async def get_drugs(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.get_allowed_drugs_info(user_id=user.id)


@user_router.post(path="/tokens", description="Добавление токенов")
async def add_tokens(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        cache_service: Annotated[CacheService, Depends(get_cache_service)],
        request: AddTokensRequest
):
    await user_service.add_tokens(
        user.id,
        amount_search_tokens=request.amount_search_tokens,
        amount_question_tokens=request.amount_question_tokens
    )
    await cache_service.redis_service.invalidate_user_data(telegram_id=user.telegram_id)


@user_router.post(path="/description", description="Обновить описание пользователя")
async def update_description(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        user_service: Annotated[UserService, Depends(get_user_service_with_assistant)],
):
    await user_service.update_user_description(user.id)
