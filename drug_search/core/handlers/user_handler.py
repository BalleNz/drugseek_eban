from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from drug_search.core.schemas import UserSchema
from drug_search.core.schemas.API_schemas.api_requests import AddTokensRequest
from drug_search.core.services.user_service import UserService, get_user_service
from drug_search.core.utils.auth import get_auth_user

user_router = APIRouter(prefix="/user")


@user_router.get(
    path="/",
    response_model=UserSchema
)
async def get_me(
        user: Annotated[UserSchema, Depends(get_auth_user)],
):
    return user


# TODO: GET allowed drugs (list with name_ru)
@user_router.get(path="/allowed_drugs", description="Получение всех ID и drug_name_ru разрешенных пользователю")
async def allowed_drug_ids_ru_names(
        user: Annotated[UserSchema, Depends(get_auth_user)],

):
    ...


@user_router.put(path="/add_tokens", description="Добавление токенов")
async def add_tokens(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        request_body: AddTokensRequest
):
    await user_service.reduce_tokens(user.id, -request_body.tokens_amount)
