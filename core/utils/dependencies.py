from fastapi import HTTPException, Depends, Request

from services.user_service import UserService, get_user_service
from schemas.user import UserSchema


async def get_telegram_user(
        request: Request,
        user_service: UserService = Depends(get_user_service)
) -> UserSchema:
    update = await request.json()

    if "message" not in update:
        raise HTTPException(status_code=400, detail="Invalid Telegram update")

    chat_id = update["message"]["chat"]["id"]
    user = await user_service.get_or_create_user(telegram_id=chat_id)
    return user
