from fastapi import FastAPI
import uvicorn

from config import config
from handlers import user_router, auth_router
from handlers.drug_handler import drug_router
from schemas.API_schemas.O2AuthSchema import jwt_openapi


def get_app() -> FastAPI:
    app = FastAPI(
        title="DrugSearch API",
    )

    # routers
    app.include_router(drug_router, prefix="/v1", tags=["Drugs"])
    app.include_router(user_router, prefix="/v1", tags=["User"])
    app.include_router(auth_router, prefix="/v1", tags=["Auth"])

    # custom auth schema after including routers
    app.openapi = lambda: jwt_openapi(app)

    return app


fastapi_app = get_app()

if __name__ == "__main__":
    uvicorn.run(
        app=fastapi_app,
        host=config.WEBAPP_HOST,
        port=config.WEBAPP_PORT,
    )
