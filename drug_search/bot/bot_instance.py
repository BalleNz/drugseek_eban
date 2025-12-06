import aiogram
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from drug_search.config import config

bot = aiogram.Bot(
    token=config.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)