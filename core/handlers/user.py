from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.params import Path

from database.models.user import User
from services.user import UserService, get_user_service

user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.post(path="/allow_drug/{drug_id}")
async def allow_drug_to_user(
        user: User = ...,  # TODO: auth
        drug_id: UUID = Path(),
        user_service: UserService = Depends(get_user_service),
):
    await user_service.allow_drug_to_user(user=user, drug_id=drug_id)


@user_router.get(path="/", response_model=User)
async def get_me(
        user: User = ...
):
    return user
