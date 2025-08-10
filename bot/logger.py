import logging
from pathlib import Path


def setup_logging():
    """Настройка логгера для всего приложения"""
    logger = logging.getLogger("bot")
    logger.info("Logger initialized")
    return logger


# Глобальный логгер (можно импортировать в других модулях)
bot_logger = setup_logging()
