from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from drug_search.bot.keyboards.callbacks import InfoSectionCallback
from drug_search.bot.keyboards.other_keyboards import get_modes_information_keyboard
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.bot.lexicon.materials.get_file import get_file_by_name
from drug_search.bot.lexicon.message_text import MessageText

router = Router(name=__name__)


@router.message(F.text == ButtonText.MODES_INFO)
async def modes_info_main(
        message: Message,
        state: FSMContext,  # noqa
):
    keyboard = get_modes_information_keyboard()

    await message.answer(
        text=MessageText.QUERIES,
        reply_markup=keyboard
    )


@router.callback_query(InfoSectionCallback.filter())
async def modes_info_listing(
    callback_query: CallbackQuery,
    callback_data: InfoSectionCallback,
    state: FSMContext  # noqa
):
    mode: str = callback_data.mode
    keyboard = get_modes_information_keyboard(
        mode=mode
    )

    message_text: str = ""
    file_path: str = ""
    match mode:
        case ButtonText.MODES_INFO_PHARMA:
            message_text = MessageText.QUERIES_PHARMA
            file_path = get_file_by_name("question_pharma_faq.jpeg")

        case ButtonText.MODES_INFO_QUESTIONS:
            message_text = MessageText.QUERIES_QUESTIONS
            file_path = get_file_by_name("question_faq.jpeg")

        case ButtonText.MODES_INFO_DRUG_SEARCH:
            message_text = MessageText.QUERIES_DRUG_SEARCH
            file_path = get_file_by_name("drug_search_faq.png")

    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=file_path,  # Прямо через open()
            caption=message_text
        ),
        reply_markup=keyboard
    )