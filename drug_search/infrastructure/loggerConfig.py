import sys
from logging.config import dictConfig


def configure_logging():
    """Настройка логирования"""
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": sys.stdout,
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
        "loggers": {
            "arq": {
                "level": "INFO",
                "propagate": True
            },
            "drug_search": {
                "level": "INFO",
                "propagate": True
            }
        }
    })
