from fastapi import HTTPException, Depends, Request

from drug_search.core.services.user_service import UserService, get_user_service
from drug_search.core.schemas.user_schemas import UserSchema
from drug_search.core.schemas import UserTelegramDataSchema


async def get_telegram_user(
        request: Request,
        user_service: UserService = Depends(get_user_service)
) -> UserSchema:
    update = await request.json()

    if "message" not in update:
        raise HTTPException(status_code=400, detail="Invalid Telegram update")

    chat_id = update["message"]["chat"]["id"]

    telegram_user: UserTelegramDataSchema = UserTelegramDataSchema(
        None,  # TODO
    )
    user: UserSchema = await user_service.repo.get_or_create_from_telegram(telegram_user=telegram_user)
    return user
