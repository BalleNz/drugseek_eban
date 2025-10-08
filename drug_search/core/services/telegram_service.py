import aiohttp
from aiogram.types import ReplyKeyboardMarkup

from drug_search.config import config
from drug_search.core.schemas import DrugSchema
from drug_search.core.utils.message_templates import MessageTemplates


class TelegramService:
    """Сервис для отправки сообщений через Telegram Bot API"""

    def __init__(self):
        """Инициализация сервиса"""
        self.api_url = f"{config.TELEGRAM_API_URL}{config.TELEGRAM_BOT_TOKEN}"

    async def send_message(
            self,
            user_telegram_id: str,
            message: str,
            reply_markup: ReplyKeyboardMarkup = None  # keyboard
    ):
        """Отправляет сообщение юзеру"""
        url = f"{self.api_url}/sendMessage"
        data = {
            "chat_id": user_telegram_id,
            "text": message,
            "parse_mode": "HTML"
        }

        if reply_markup:
            import json
            data["reply_markup"] = json.dumps(reply_markup)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                if response.status != 200:
                    response_text = await response.text()
                    raise ValueError(f"Ошибка отправки сообщения в Telegram: {response.status} - {response_text}")

    async def edit_message(
            self,
            old_message_id: str,
            user_telegram_id: str,
            message_text: str,
            reply_markup: ReplyKeyboardMarkup | None = None,
            parse_mode: str = "HTML"
    ):
        """Редактирует сообщение"""
        url: str = f"{self.api_url}/editMessageText"
        data = {
            "chat_id": user_telegram_id,
            "message_id": old_message_id,
            "text": message_text,
            "parse_mode": parse_mode
        }

        if reply_markup:
            import json
            data["reply_markup"] = json.dumps(reply_markup)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                if response.status != 200:
                    response_text = await response.text()
                    raise ValueError(f"Ошибка отправки сообщения в Telegram: {response.status} - {response_text}")

    async def send_drug_created_notification(
            self,
            user_telegram_id: str,
            drug: DrugSchema,
    ):
        """Отправляет сообщение о созданном препарате с клавиатурой"""
        message = MessageTemplates.DRUG_CREATED_JOB_FINISHED.format(name_ru=drug.name_ru)
        await self.send_message(user_telegram_id, message=message, reply_markup=None)
