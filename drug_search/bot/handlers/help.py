import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions

from drug_search.bot.keyboards.callbacks import HelpSectionCallback
from drug_search.bot.keyboards.other_keyboards import get_help_keyboard
from drug_search.bot.lexicon.enums import HelpSectionMode
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.bot.lexicon.message_text import MessageText

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
