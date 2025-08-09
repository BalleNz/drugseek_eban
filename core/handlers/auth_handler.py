from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from schemas import UserTelegramDataSchema
from services.user_service import UserService, get_user_service
from utils import auth

auth_router = APIRouter(prefix="/telegram_auth")


@auth_router.post("/")
async def telegram_auth(
        telegram_user_data: UserTelegramDataSchema,
        user_service: UserService = Depends(get_user_service)
):
    """
    Авторизирует или регистрирует нового пользователя.

    Возращает JWT токен.
    """
    try:
        user_data = await user_service.repo.get_or_create_from_telegram(telegram_user_data)
        return {
            "token": await auth.generate_jwt(user_data.id, user_data.telegram_id)
        }

    except HTTPException as ex:
        return JSONResponse(
            status_code=ex.status_code,
            content={"detail": ex.detail}
        )
