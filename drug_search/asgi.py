import uvicorn

from drug_search.config import config
from drug_search.core.app.main import fastapi_app
from drug_search.infrastructure.loggerConfig import configure_logging

# FASTAPI APP
app = fastapi_app

# TELEGRAM BOT
bot = ...

if __name__ == "__main__":
    configure_logging()
    uvicorn.run(
        app=fastapi_app,
        host=config.WEBAPP_HOST,
        port=config.WEBAPP_PORT,
    )
