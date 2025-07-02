from dotenv import dotenv_values

env = dotenv_values("../.env")

class Config:
    DEBUG_MODE: bool = True

    # DATABASE SETTINGS
    DATABASE_URL: str = env.get("DATABASE_URL", "")

    # BOT SETTINGS
    ...

config = Config()
