import logging
import re

from aiogram import Router
from aiogram.types import BufferedInputFile, CallbackQuery

from drug_search.bot.keyboards.callbacks import ExportPdfCallback
from drug_search.bot.lexicon.message_text import MessageText
from drug_search.core.lexicon import BOT_USERNAME
from drug_search.core.schemas import DrugSchema
from drug_search.core.services.cache_logic.cache_service import CacheService
from drug_search.core.services.pdf.drug_pdf_generator import DrugPdfGenerator
from drug_search.core.utils.referrals_funcs import generate_referral_url

router = Router(name=__name__)
logger = logging.getLogger(__name__)


def _safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", name, flags=re.UNICODE).strip()
    return (cleaned or "drug")[:60] + ".pdf"


@router.callback_query(ExportPdfCallback.filter())
async def export_drug_pdf(
        callback_query: CallbackQuery,
        callback_data: ExportPdfCallback,
        cache_service: CacheService,
        access_token: str,
):
    await callback_query.answer("⏳ Создаём Pharma Card PDF…")

    drug: DrugSchema = await cache_service.get_drug(
        access_token=access_token,
        drug_id=callback_data.drug_id,
    )

    referral_url = generate_referral_url(
        user_id=str(callback_query.from_user.id),
        bot_username=BOT_USERNAME,
    )

    try:
        pdf_bytes = DrugPdfGenerator().generate(
            drug=drug,
            referral_url=referral_url,
            bot_username=BOT_USERNAME,
        )
    except Exception as exc:
        logger.exception("PDF generation failed: %s", exc)
        await callback_query.message.answer(MessageText.PDF_GENERATION_ERROR)
        return

    display_name = drug.name_ru or drug.name
    await callback_query.message.answer_document(
        document=BufferedInputFile(pdf_bytes, filename=_safe_filename(display_name)),
        caption=MessageText.PDF_READY.format(drug_name=display_name),
    )
