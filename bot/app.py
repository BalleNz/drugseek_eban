# bot/bot.py
import aiogram
from aiogram import Dispatcher
from bot.middlewares.auth import AuthMiddleware
from bot.handlers.auth import handle_webapp_auth
from core.config import config

def setup_auth(dp: Dispatcher):
    # Регистрация middleware
    dp.update.outer_middleware(AuthMiddleware())

    # Регистрация хендлеров
    dp.message.register(handle_webapp_auth, web_app_data=True)
    dp.message.register(login_handler, Command("login"))


bot = aiogram.Bot(token=config.BOT_TOKEN)


if __name__ == "__main__":
    ...
