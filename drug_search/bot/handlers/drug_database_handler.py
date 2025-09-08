import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.bot.keyboards import DrugDescribeCallback
from drug_search.bot.keyboards import DrugListCallback
from drug_search.bot.keyboards.keyboard_markups import drug_database_get_full_list, get_drugs_list_keyboard
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.bot.states.states import States
from drug_search.core.services.redis_service import redis_service
from schemas.telegram_schemas import AllowedDrugsSchema
from services.redis_service import RedisService

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.message(F.text == ButtonText.DRUG_DATABASE)
async def drug_menu_handler(
        message: Message,
        redis_service: RedisService,
        state: FSMContext,
):
    await state.set_state(States.DRUG_DATABASE_MENU)

    user_id = message.from_user.id

    cache_key = f"user:{user_id}:allowed_drugs_info"  # TODO там будет храниться массив из разрешенных + скока всего в базе
    allowed_drugs_info: AllowedDrugsSchema = await redis_service.get_cached_or_fetch(
        cache_key=cache_key
    )

    # TODO: сообщение со статистикой + клавиатура drug_database_get_full_list
    await message.answer(
        text=...,
        reply_markup=drug_database_get_full_list
    )


@router.callback_query(DrugListCallback.filter(), States.DRUG_DATABASE_MENU)
async def drug_list_handler(
        callback: CallbackQuery,
        redis_service: RedisService,
        callback_data: DrugListCallback,
):
    user_id = callback.from_user.id

    cache_key = f"user:{user_id}:allowed_drugs_info"
    allowed_drugs_info: AllowedDrugsSchema = await redis_service.get_cached_or_fetch(
        cache_key=cache_key
    )

    # TODO: отправляем сообщение с клавиатурой
    await callback.message.edit_text(
        text=...,
        reply_markup=get_drugs_list_keyboard(
            drugs=allowed_drugs_info.allowed_drugs,
            page=callback_data.page
        )
    )


@router.callback_query(DrugDescribeCallback.filter(), States.DRUG_DATABASE_MENU)
async def drug_describe_handler(
        callback: CallbackQuery,
        redis_service: RedisService,
        callback_data: DrugDescribeCallback,
        state: FSMContext
):
    await state.set_state(States.DRUG_DATABASE_DESCRIBE)

    user_id = callback.from_user.id

    # callback data
    drug_id = callback_data.drug_id

    # redis
    cache_key = f"user:{user_id}:drug_describe:{drug_id}"
    drug_description = redis_service.get_cached_or_fetch(
        cache_key=cache_key,
        drug_id=drug_id
    )

    # TODO: отправляем сообщение с описанием препарата и клавой (выбор описания)
    await callback.message.edit_text(
        text=...,
        reply_markup=...
    )
