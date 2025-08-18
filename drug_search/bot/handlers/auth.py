# bot/handlers/auth_handler.py
from aiogram.types import Update
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.web_app import safe_parse_webapp_init_data

from drug_search.bot.api_client import AsyncHttpClient


async def handle_webapp_auth(
        update: Update,
        context: ..., # ContextTypes.DEFAULT_TYPE,
        api_client: AsyncHttpClient = ...,
):
    """Обработка данных аутентификации из WebApp"""
    try:
        # 1. Проверяем, что это данные от Telegram WebApp
        if not update.message or not update.message.web_app_data:
            return await update.message.reply_text("Используйте кнопку WebApp для входа")

        # 2. Парсим и валидируем данные
        init_data = safe_parse_webapp_init_data(
            token=context.bot.token,
            init_data=update.message.web_app_data.data
        )

        # 3. Отправляем на бэкенд для создания JWT
        response = await api_client.login_via_telegram(  # TODO
            telegram_id=init_data.user.id,
            first_name=init_data.user.first_name,
            last_name=init_data.user.last_name,
            username=init_data.user.username
        )

        # 4. Сохраняем токен в FSM
        await update.message.delete()  # Удаляем сообщение с чувствительными данными
        state = FSMContext(context.bot, update.chat.id, update.from_user.id)
        await state.update_data(access_token=response.token)

        await update.message.answer("✅ Вы успешно авторизованы!")

    except Exception as e:
        await update.message.answer(f"🚫 Ошибка авторизации: {str(e)}")
