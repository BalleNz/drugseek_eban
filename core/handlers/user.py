from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.params import Path

from database.models.user import User
from services.user import UserService, get_user_service

user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.get(path="/", response_model=User)
async def get_me(
        user: User = ...
):
    return user
