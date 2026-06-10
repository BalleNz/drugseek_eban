from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from drug_search.bot.keyboards.callbacks import QuickStartCallback


def start_wow_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🧠 Викторина",
                    callback_data=QuickStartCallback(action="quiz").pack(),
                ),
                InlineKeyboardButton(
                    text="📄 PDF-карточка",
                    callback_data=QuickStartCallback(action="pdf_hint").pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🎁 Бесплатные токены",
                    callback_data=QuickStartCallback(action="free_tokens").pack(),
                ),
            ],
        ]
    )
