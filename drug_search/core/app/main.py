from fastapi import FastAPI

from drug_search.core.handlers import (user_router, auth_router, drug_router,
                                       assistant_router, admin_router, referrals_router)
from drug_search.core.schemas.API_schemas.O2AuthSchema import jwt_openapi


def get_app() -> FastAPI:
    app: FastAPI = FastAPI(
        title="DrugSearch API",
        lifespan=None
    )

    # routers
    app.include_router(drug_router, prefix="/v1", tags=["Drugs"])
    app.include_router(user_router, prefix="/v1", tags=["User"])
    app.include_router(auth_router, prefix="/v1", tags=["Auth"])
    app.include_router(assistant_router, prefix="/v1", tags=["Assistant"])
    app.include_router(admin_router, prefix="/v1", tags=["Admin"])
    app.include_router(referrals_router, prefix="/v1", tags=["Referrals"])

    # custom auth schema after including routers
    app.openapi = lambda: jwt_openapi(app)

    return app


fastapi_app: FastAPI = get_app()
