from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.params import Body
from fastapi.responses import JSONResponse

from services.user import UserService, get_user_service
from utils import auth

auth_router = APIRouter(prefix="/webapp_auth", tags=["WebAppAuth"])


@auth_router.post("/webapp/auth")
async def webapp_auth(
        init_data: str = Body(..., embed=True),
        user_service: UserService = Depends(get_user_service)
):
    try:
        user_data = await auth.verify_telegram_data(init_data)
        user = await user_service.get_or_create_from_telegram(user_data)

        return {
            "token": await auth.generate_jwt(user_data["user"]),
            "user": user
        }
    except HTTPException as ex:
        return JSONResponse(
            status_code=ex.status_code,
            content={"detail": ex.detail}
        )
