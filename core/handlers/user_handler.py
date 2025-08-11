from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.security import HTTPBearer

from schemas import UserSchema
from utils.auth import get_auth_user

user_router = APIRouter(prefix="/user")


@user_router.get(
    path="/",
    response_model=UserSchema
)
async def get_me(
        user: UserSchema = Depends(get_auth_user)
):
    return user

# TODO: GET allowed drugs (list with name_ru)
