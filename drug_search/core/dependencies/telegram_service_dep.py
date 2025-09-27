from drug_search.core.services.telegram_service import TelegramService

telegram_service = TelegramService()


def get_telegram_service():
    """Возвращает синглтон TelegramService"""
    return telegram_service
