from fastapi import APIRouter
from fastapi.params import Body

from schemas import UserSchema

user_router = APIRouter(prefix="/user")


@user_router.get(path="/", response_model=UserSchema)
async def get_me(
        user: UserSchema = Body()
):
    return user
