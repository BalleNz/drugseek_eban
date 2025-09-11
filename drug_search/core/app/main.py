from fastapi import FastAPI
import uvicorn

from drug_search.config import config
from drug_search.core.handlers import user_router, auth_router
from drug_search.core.handlers.drug_handler import drug_router
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

    # custom auth schema after including routers
    app.openapi = lambda: jwt_openapi(app)

    return app


fastapi_app: FastAPI = get_app()
