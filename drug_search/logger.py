import logging
from logging import Logger


def setup_logging() -> Logger:
    """Настройка логгера для всего приложения"""
    logger = logging.getLogger()
    logger.info("Logger initialized")
    return logger


# Глобальный логгер (можно импортировать в других модулях)
logger: Logger = setup_logging()
