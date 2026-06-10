from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from drug_search.core.handlers import (user_router, auth_router, drug_router,
                                       assistant_router, admin_router, referrals_router, payment_router,
                                       quiz_router, pathway_router)
from drug_search.core.schemas.API_schemas.O2AuthSchema import jwt_openapi
from drug_search.core.utils.auth import validate_api_key


def get_app() -> FastAPI:
    app: FastAPI = FastAPI(
        title="DrugSearch API",
        lifespan=None,
        dependencies=[Depends(validate_api_key)],
    )

    @app.get("/health", include_in_schema=False)
    async def health():
        return {"status": "ok"}

    # routers
    app.include_router(drug_router, prefix="/v1", tags=["Drugs"])
    app.include_router(user_router, prefix="/v1", tags=["User"])
    app.include_router(auth_router, prefix="/v1", tags=["Auth"])
    app.include_router(assistant_router, prefix="/v1", tags=["Assistant"])
    app.include_router(admin_router, prefix="/v1", tags=["Admin"])
    app.include_router(referrals_router, prefix="/v1", tags=["Referrals"])
    app.include_router(payment_router, prefix="/v1", tags=["Payment"])
    app.include_router(quiz_router, prefix="/v1", tags=["Quiz"])
    app.include_router(pathway_router, prefix="/v1", tags=["Pathways"])

    webapp_dir = Path(__file__).resolve().parents[2] / "webapp"
    if webapp_dir.exists():
        app.mount("/webapp", StaticFiles(directory=str(webapp_dir), html=True), name="webapp")

    # custom auth schema after including routers
    app.openapi = lambda: jwt_openapi(app)

    return app


fastapi_app: FastAPI = get_app()
