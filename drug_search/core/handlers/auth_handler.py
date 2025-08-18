from fastapi import APIRouter, Body, Depends
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from drug_search.core.schemas.API_schemas.api_requests import UserTelegramDataSchema
from drug_search.core.services.user_service import UserService, get_user_service
from drug_search.core.utils import auth

auth_router = APIRouter(prefix="/auth")


@auth_router.post(
    "/",
    summary="Getting JWT from telegram data.",
    description="Endpoint is needed to get access token from telegram.",
    responses={
        "200": {
            "description": "Successful authentication. Returns the access token.",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "access_token": {
                                "type": "string",
                                "description": "The Telegram Access Token.",
                            },
                            "token_type": {
                                "type": "string",
                                "example": "bearer",
                            },
                        },
                        "required": ["access_token"],
                    }
                }
            },
        },
        "400": {
            "description": "Invalid Telegram authentication data.",
            "content": {"application/json": {"example": {"detail": "Invalid Telegram auth data"}}},
        },
        "500": {"description": "Internal server error"}
    }
)
async def telegram_auth(
        telegram_user_data: UserTelegramDataSchema = Body(
            ...,
            examples=[
                {
                    "telegram_id": "123456789",
                    "username": "johndoe",
                    "first_name": "John",
                    "last_name": "Doe",
                    "photo_url": "https://t.me/i/userpic/123/johndoe.jpg"
                }
            ]
        ),
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
