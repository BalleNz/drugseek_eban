from fastapi import FastAPI
import uvicorn

from config import config
from handlers import user_router, auth_router
from handlers.drug_handler import drug_router


def get_app() -> FastAPI:
    app = FastAPI(
        title="DrugSearch API"
    )

    app.include_router(drug_router, prefix="/v1", tags=["Drugs"])
    app.include_router(user_router, prefix="/v1", tags=["User"])
    app.include_router(auth_router, prefix="/v1", tags=["Auth"])
    return app


app = get_app()

if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host=config.WEBAPP_HOST,
        port=config.WEBAPP_PORT,
    )
