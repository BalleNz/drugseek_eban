from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from drug_search.bot.keyboards.callbacks import QuizAnswerCallback, QuizNextCallback
from drug_search.bot.utils.share import build_quiz_share_text, build_telegram_share_url
from drug_search.core.schemas.quiz_schemas import QuizOptionSchema


def quiz_options_keyboard(quiz_id: str, options: list[QuizOptionSchema]) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=option.name,
                callback_data=QuizAnswerCallback(
                    quiz_id=quiz_id,
                    drug_id=option.drug_id,
                ).pack(),
            )
        ]
        for option in options
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def quiz_next_keyboard(
        streak: int = 0,
        best_streak: int = 0,
        level_title: str = "",
) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text="Следующий вопрос →",
                callback_data=QuizNextCallback().pack(),
            )
        ]
    ]

    if streak > 0 and level_title:
        share_text = build_quiz_share_text(streak, level_title, best_streak)
        rows.append([
            InlineKeyboardButton(
                text="📤 Хвастаться серией",
                url=build_telegram_share_url(share_text),
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=rows)
