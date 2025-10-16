import json

import aiohttp
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup

from drug_search.bot.keyboards.keyboard_markups import question_continue_keyboard
from drug_search.config import config
from drug_search.core.lexicon import ARROW_TYPES
from drug_search.core.schemas import DrugSchema, QuestionAssistantResponse
from drug_search.core.utils.formatter import ARQMessageTemplates
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
            reply_markup: InlineKeyboardMarkup | None = None,
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
            # Ручная сериализация, чтобы избежать проблем с None значениями
            keyboard_data = {
                "inline_keyboard": [
                    [
                        {
                            "text": button.text,
                            "callback_data": button.callback_data
                            # Не включаем url, web_app и другие поля если они None
                        }
                        for button in row
                    ]
                    for row in reply_markup.inline_keyboard
                ]
            }
            data["reply_markup"] = json.dumps(keyboard_data)

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
        message: str = MessageTemplates.DRUG_CREATED_NOTIFICATION.format(name_ru=drug.name_ru)
        await self.send_message(user_telegram_id, message=message, reply_markup=None)

    async def send_drug_updated_notification(
            self,
            user_telegram_id: str,
            drug: DrugSchema,
    ):
        """Оповещение об обновлении препарата"""
        message: str = MessageTemplates.DRUG_UPDATED_NOTIFICATION.format(name_ru=drug.name_ru)
        await self.send_message(user_telegram_id, message=message, reply_markup=None)

    async def edit_message_with_assistant_answer(
            self,
            question_response: QuestionAssistantResponse,
            user_telegram_id: str,
            old_message_id: str,
            question: str,
            arrow: ARROW_TYPES
    ):
        """Редактирует сообщение для ответа на вопрос юзера"""
        message_text: str = ARQMessageTemplates.format_assistant_answer(question_response, arrow)

        await self.edit_message(
            user_telegram_id=user_telegram_id,
            old_message_id=old_message_id,
            message_text=message_text,
            reply_markup=question_continue_keyboard(
                question=question,
                arrow=arrow
            )
        )
