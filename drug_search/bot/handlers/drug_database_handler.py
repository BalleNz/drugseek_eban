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

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.message(F.text == ButtonText.DRUG_DATABASE)
async def drug_menu_handler(
        message: Message,
        api_client: DrugSearchAPIClient,
        state: FSMContext,
):
    await state.set_state(States.DRUG_DATABASE_MENU)

    user_id = message.from_user.id

    redis_key = f"user:{user_id}:allowed_drugs_info"  # TODO там будет храниться массив из разрешенных + скока всего в базе
    allowed_drugs_info: AllowedDrugsSchema = redis_service.get_cached_or_fetch(redis_key, api_client)

    # TODO: сообщение со статистикой + клавиатура drug_database_get_full_list
    await message.answer(text=..., reply_markup=drug_database_get_full_list)


@router.callback_query(DrugListCallback.filter(), States.DRUG_DATABASE_MENU)
async def drug_list_handler(
        callback: CallbackQuery,
        api_client: DrugSearchAPIClient,
        callback_data: DrugListCallback,
):
    user_id = callback.from_user.id

    redis_key = f"user:{user_id}:allowed_drugs_info"
    allowed_drugs_info: AllowedDrugsSchema = redis_service.get_cached_or_fetch(redis_key, api_client)

    # TODO: отправляем сообщение с клавиатурой
    await callback.message.edit_text(
        text=...,
        reply_markup=get_drugs_list_keyboard(
            drugs=cached_drugs_briefly.allowed_drugs,
            page=callback_data.page
        )
    )


@router.callback_query(DrugDescribeCallback.filter(), States.DRUG_DATABASE_MENU)
async def drug_describe_handler(
        callback: CallbackQuery,
        api_client: DrugSearchAPIClient,
        callback_data: DrugDescribeCallback,
        state: FSMContext
):
    await state.set_state(States.DRUG_DATABASE_DESCRIBE)

    user_id = callback.from_user.id

    # callback data
    drug_id = callback_data.drug_id

    # redis
    redis_key = f"user:{user_id}:drug_describe:{drug_id}"
    cached_drugs_briefly = redis_service.get_cached_or_fetch(redis_key, api_client)

    # TODO: отправляем сообщение с описанием препарата и клавой (выбор описания)
    ...
