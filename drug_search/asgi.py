import uvicorn

from drug_search.config import config
from drug_search.core.app import fastapi_app

# FASTAPI APP
app = fastapi_app

# TELEGRAM BOT
bot = ...

if __name__ == "__main__":
    uvicorn.run(
        app=fastapi_app,
        host=config.WEBAPP_HOST,
        port=config.WEBAPP_PORT,
    )