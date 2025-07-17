import FastAPI
import uvicorn

from handlers.drug import drug_router


def get_app() -> FastAPI:
    app = FastAPI(
        title="DrugSearch API"
    )

    app.include_router(drug_router, prefix="/drugs", tags=["drugs"])
    return app

app = get_app()

if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host=...,
        port=...,
    )
