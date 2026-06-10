import logging

from aiogram import Router
from aiogram.types import CallbackQuery

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.bot.handlers.quiz import start_quiz
from drug_search.bot.keyboards.callbacks import QuickStartCallback
from drug_search.bot.keyboards.start_keyboards import start_wow_keyboard
from drug_search.bot.lexicon.message_text import MessageText
from drug_search.core.services.cache_logic.cache_service import CacheService

router = Router(name=__name__)
logger = logging.getLogger(__name__)


@router.callback_query(QuickStartCallback.filter())
async def quick_start_actions(
        callback_query: CallbackQuery,
        callback_data: QuickStartCallback,
        access_token: str,
        api_client: DrugSearchAPIClient,
        cache_service: CacheService,
):
    await callback_query.answer()

    match callback_data.action:
        case "quiz":
            await start_quiz(callback_query, access_token, api_client, cache_service)
        case "pdf_hint":
            await callback_query.message.answer(
                "📄 <b>Pharma Card PDF</b>\n\n"
                "Найди любой препарат в базе — на карточке появятся кнопки "
                "«📄 Pharma Card PDF» и «📤 Поделиться».\n\n"
                "PDF в бело-синем стиле с летающими шприцами 💉 — идеально для шеринга.",
                reply_markup=start_wow_keyboard(),
            )
        case "free_tokens":
            await callback_query.message.answer(MessageText.FREE_TOKENS_INFO)
