import logging
from pathlib import Path

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions, InputMediaVideo, InputFile, InputMediaPhoto

from drug_search.bot.keyboards.callbacks import HelpSectionCallback
from drug_search.bot.keyboards.keyboard_markups import get_help_keyboard
from drug_search.bot.lexicon.enums import HelpSectionMode
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.bot.lexicon.message_text import MessageText
from utils.materials.get_file import get_file_by_name

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.callback_query(HelpSectionCallback.filter())
async def help_listing(
        callback_query: CallbackQuery,
        callback_data: HelpSectionCallback,
        state: FSMContext  # noqa
):
    """Листать помощь"""
    await callback_query.answer()

    file_path: str = ""
    match callback_data.mode:
        case HelpSectionMode.QUERIES_DRUG_SEARCH:
            file_path = get_file_by_name("drug_search_faq.png")
        case HelpSectionMode.QUERIES_QUESTIONS:
            file_path = get_file_by_name("question_faq.jpeg")
        case HelpSectionMode.QUERIES_PHARMA_QUESTIONS:
            file_path = get_file_by_name("question_pharma_faq.jpeg")

    if file_path:
        await callback_query.message.edit_media(
            media=InputMediaPhoto(
                media=file_path,  # Прямо через open()
                caption=MessageText.help.help_format_by_mode[callback_data.mode]
            ),
            reply_markup=get_help_keyboard(help_mode=callback_data.mode)
        )
    else:
        if not callback_query.message.text:
            await callback_query.message.delete()
            await callback_query.message.answer(
                text=MessageText.help.help_format_by_mode[callback_data.mode],
                reply_markup=get_help_keyboard(help_mode=callback_data.mode),
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
        else:
            await callback_query.message.edit_text(
                text=MessageText.help.help_format_by_mode[callback_data.mode],
                reply_markup=get_help_keyboard(help_mode=callback_data.mode),
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
    await callback_query.answer()


@router.message(F.text == ButtonText.HELP)
async def get_help(
        message: Message,
        state: FSMContext,  # noqa
):
    await message.answer(
        text=MessageText.help.MAIN,
        reply_markup=get_help_keyboard(
            help_mode=HelpSectionMode.MAIN
        ),
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
