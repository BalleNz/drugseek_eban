import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage import redis
from aiogram.types import Message, CallbackQuery

from drug_search.bot.keyboards import DrugDescribeCallback
from drug_search.bot.keyboards import DrugListCallback
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.bot.states.states import States
from keyboards.keyboard_markups import drug_database_get_full_list
from services.redis_service import redis_service

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.message(F.text == ButtonText.DRUG_DATABASE)
async def drug_menu_handler(message: Message, state: FSMContext):
    await state.set_state(States.DRUG_DATABASE_MENU)

    user_id = message.from_user.id

    # redis
    redis_key = f"user:{user_id}:allowed_drugs"  # TODO там будет храниться массив из разрешенных + скока всего в базе
    cached_drugs_briefly = redis_service.get_cached_or_fetch(redis_key)

    # TODO: сообщение со статистикой + клавиатура drug_database_get_full_list
    await message.answer(text=..., reply_markup=drug_database_get_full_list)


@router.callback_query(DrugListCallback.filter(), States.DRUG_DATABASE_MENU)
async def drug_list_handler(callback: CallbackQuery, callback_data: DrugListCallback):
    user_id = callback.from_user.id

    # redis
    redis_key = f"user:{user_id}:allowed_drugs"

    cached_drugs_briefly = redis_service.get_cached_or_fetch(redis_key)
    # TODO: отправляем сообщение с клавиатурой
    ...


@router.callback_query(DrugDescribeCallback.filter(), States.DRUG_DATABASE_MENU)
async def drug_describe_handler(callback: CallbackQuery, callback_data: DrugDescribeCallback, state: FSMContext):
    await state.set_state(States.DRUG_DATABASE_DESCRIBE)

    user_id = callback.from_user.id

    # callback data
    drug_id = callback_data.drug_id

    # redis
    if callback_data.briefly:
        redis_key = f"user:{user_id}:drug_briefly:{drug_id}"
    else:
        redis_key = f"user:{user_id}:drug_describe:{drug_id}"
    cached_drugs_briefly = redis_service.get_cached_or_fetch(redis_key)

    # TODO: отправляем сообщение с описанием препарата и клавой (выбор описания)
    ...
