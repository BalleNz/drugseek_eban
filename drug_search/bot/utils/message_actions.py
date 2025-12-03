import asyncio
import logging

from aiogram.types import Message, LinkPreviewOptions

from drug_search.bot.keyboards import drug_keyboard
from drug_search.bot.lexicon.enums import ModeTypes
from drug_search.bot.utils.format_message_text import DrugMessageFormatter
from drug_search.core.lexicon.enums import DrugMenu
from drug_search.core.schemas import DrugSchema, UserSchema

logger = logging.getLogger(name=__name__)


async def delete_message_after_delay(message: Message, delay: int = 30):
    """Фоновая задача для удаления сообщения через указанное время"""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение: {e}")


async def open_drug_menu(
        drug: DrugSchema,
        drug_menu: DrugMenu | None,
        message: Message,
        user: UserSchema
):
    """Открывает меню с препаратом"""
    message_text = DrugMessageFormatter.format_by_type(
        drug_menu=drug_menu,
        drug=drug
    )
    await message.answer(
        message_text,
        reply_markup=drug_keyboard(
            drug=drug,
            mode=ModeTypes.SEARCH,
            drug_menu=drug_menu,
            user_subscribe_type=user.subscription_type,
            user_query=message.text
        ),
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
