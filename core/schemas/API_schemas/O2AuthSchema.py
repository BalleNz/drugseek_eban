from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def jwt_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="DrugSeek API",
        version="1.0.0",
        description="Приложение позволяет делать запросы зарегистрированным пользователям "
                    "для поиска подробного описания препаратов в DeepSeek",
        routes=app.routes
    )

    openapi_schema["components"]["securitySchemes"] = {
        "TelegramAccessToken": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Auth via JWT-Token."
        }
    }
    openapi_schema["security"] = [{"TelegramAccessToken": []}]
    for path in openapi_schema["paths"]:
        if path != "/v1/auth" and not path.startswith("/docs"):
            openapi_schema["paths"][path]["security"] = [{"TelegramAccessToken": []}]

    return openapi_schema
