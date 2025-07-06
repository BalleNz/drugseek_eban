import logging
from pathlib import Path


def setup_logging():
    """Настройка логгера для всего приложения"""
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "INFO"
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": Path(__file__).parent / "logs" / "bot.log",
                "formatter": "default",
                "level": "DEBUG"
            }
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "DEBUG"
        }
    })

    logger = logging.getLogger("bot")
    logger.info("Logger initialized")
    return logger


# Глобальный логгер (можно импортировать в других модулях)
bot_logger = setup_logging()
