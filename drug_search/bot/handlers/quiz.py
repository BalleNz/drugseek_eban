import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.bot.keyboards.callbacks import QuizAnswerCallback, QuizNextCallback
from drug_search.bot.keyboards.quiz_keyboards import quiz_next_keyboard, quiz_options_keyboard
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.bot.lexicon.message_text import MessageText
from drug_search.bot.utils.gamification import format_level_badge
from drug_search.core.schemas.quiz_schemas import QuizAnswerRequest, QuizQuestionResponse
from drug_search.core.services.cache_logic.cache_service import CacheService
from drug_search.core.services.gamification_service import GamificationService

router = Router(name=__name__)
logger = logging.getLogger(__name__)


async def start_quiz(
        target: Message | CallbackQuery,
        access_token: str,
        api_client: DrugSearchAPIClient,
        cache_service: CacheService,
):
    try:
        question: QuizQuestionResponse = await api_client.get_quiz_question(access_token)
    except Exception as exc:
        logger.exception("Quiz question error: %s", exc)
        text = MessageText.NO_TOKENS if "402" in str(exc) else "Не удалось загрузить вопрос. Попробуйте позже."
        if isinstance(target, CallbackQuery):
            await target.message.edit_text(text)
        else:
            await target.answer(text)
        return

    await cache_service.redis_service.invalidate_user_data(str(target.from_user.id))

    keyboard = quiz_options_keyboard(question.quiz_id, question.options)
    text = f"<b>Вопрос:</b>\n{question.question}"

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=keyboard)
    else:
        intro = f"{MessageText.QUIZ_INTRO}\n\n{text}"
        await target.answer(intro, reply_markup=keyboard)


@router.message(F.text == ButtonText.MODES_INFO_QUIZ)
@router.message(Command("quiz"))
async def quiz_from_menu(
        message: Message,
        access_token: str,
        api_client: DrugSearchAPIClient,
        cache_service: CacheService,
):
    await start_quiz(message, access_token, api_client, cache_service)


@router.callback_query(QuizNextCallback.filter())
async def quiz_next_question(
        callback_query: CallbackQuery,
        access_token: str,
        api_client: DrugSearchAPIClient,
        cache_service: CacheService,
):
    await callback_query.answer()
    await start_quiz(callback_query, access_token, api_client, cache_service)


@router.callback_query(QuizAnswerCallback.filter())
async def quiz_answer_handler(
        callback_query: CallbackQuery,
        callback_data: QuizAnswerCallback,
        access_token: str,
        api_client: DrugSearchAPIClient,
        cache_service: CacheService,
):
    await callback_query.answer()

    try:
        response = await api_client.check_quiz_answer(
            access_token,
            QuizAnswerRequest(
                quiz_id=callback_data.quiz_id,
                selected_drug_id=callback_data.drug_id,
            ),
        )
    except Exception as exc:
        logger.exception("Quiz answer error: %s", exc)
        await callback_query.message.edit_text(
            "Викторина истекла. Нажмите «Следующий вопрос».",
            reply_markup=quiz_next_keyboard(),
        )
        return

    gamification = GamificationService(cache_service.redis_service)
    stats = await gamification.record_quiz_answer(
        str(callback_query.from_user.id),
        response.is_correct,
    )
    level_badge = format_level_badge(stats.best_streak)

    if response.is_correct:
        text = MessageText.QUIZ_CORRECT
        if stats.streak >= 2:
            text += MessageText.QUIZ_STREAK_BONUS.format(
                streak=stats.streak,
                best_streak=stats.best_streak,
                level_badge=level_badge,
            )
        if stats.streak in (3, 5, 10, 15):
            text += MessageText.QUIZ_MILESTONE.format(
                streak=stats.streak,
                level_badge=level_badge,
            )
    else:
        text = MessageText.QUIZ_WRONG.format(explanation=response.explanation or "")

    await callback_query.message.edit_text(
        text,
        reply_markup=quiz_next_keyboard(
            streak=stats.streak,
            best_streak=stats.best_streak,
            level_title=level_badge,
        ),
    )
