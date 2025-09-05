# bot/bot.py
import aiogram
from aiogram import Dispatcher
from middlewares.auth_middleware import AuthMiddleware
from drug_search.config import config


def setup_auth(dp: Dispatcher):
    # Регистрация middleware
    dp.update.outer_middleware(AuthMiddleware())

    # Регистрация хендлеров
    ...


bot = aiogram.Bot(token=config.BOT_TOKEN)


if __name__ == "__main__":
    ...
