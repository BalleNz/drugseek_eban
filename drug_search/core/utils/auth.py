import logging
from datetime import datetime
from datetime import timedelta, UTC
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import HTTPException
from fastapi.params import Depends
from starlette import status

from drug_search.config import config
from drug_search.core.schemas import UserSchema
from drug_search.core.services.user_service import UserService
from drug_search.core.dependencies.user_service_dep import get_user_service

logger = logging.getLogger(__name__)


async def generate_jwt(user_id: UUID, user_tg_id: str) -> str:
    """
    Генерация JWT-токена. Возращает JWT-токен.

    :param user_id: User ID,
    :param user_tg_id: User Telegram ID
    """
    return jwt.encode(
        {
            "sub": str(user_id),
            "tg_id": user_tg_id,
            "exp": datetime.now(UTC) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRES_MINUTES)
        },
        config.SECRET_KEY,
        algorithm="HS256"
    )


async def decode_jwt(token: str) -> UUID:
    """
    Decoding jwt-token to user_id

    :param token: JWT-Token

    :returns: User ID: UUID
    """
    try:
        payload = jwt.decode(
            jwt=token,
            key=config.SECRET_KEY,
            algorithms=[config.ALGORITHM],
            options={"verify_exp": True}
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "JWT token expired!")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "JWT token invalid!")

    user_id = payload.get("sub")  # user_id
    if not user_id:
        raise HTTPException(403, "Can't get user_id from payload")
    return user_id


async def get_auth_user(
        user_service: Annotated[UserService, Depends(get_user_service)],
        token: str = Depends(config.OAUTH2_SCHEME)
) -> UserSchema:
    """
    Getting User Schema from token.

    :return: User: UserSchema
    """
    user_id: UUID = await decode_jwt(token)

    user: UserSchema = await user_service.repo.get_user(user_id)
    if not user:
        logger.exception(f"Cannot find user by token: {token}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong user.")
    return user
