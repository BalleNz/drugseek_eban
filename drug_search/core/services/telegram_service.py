import aiohttp

from drug_search.config import config


class TelegramService:
    """Сервис для отправки сообщений через Telegram Bot API"""

    def __init__(self):
        """Инициализация сервиса"""
        self.api_url = f"{config.TELEGRAM_API_URL}{config.TELEGRAM_BOT_TOKEN}"

    async def send_message(
            self,
            user_telegram_id: str,
            message: str,
            reply_markup: dict = None  # keyboard
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

    async def send_drug_created_notification(
            self,
            user_telegram_id: str,
            drug_name: str,
    ):
        """Отправляет сообщение о создании препарата с клавиатурой"""
        pass
