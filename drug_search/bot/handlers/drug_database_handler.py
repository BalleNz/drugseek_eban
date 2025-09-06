import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage import redis
from aiogram.types import Message, CallbackQuery

from drug_search.bot.keyboards import DrugBrieflyCallback, DrugDescribeCallback
from drug_search.bot.keyboards import DrugDatabaseScrollingCallback
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.bot.states.states import States

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.message(F.text == ButtonText.DRUG_DATABASE)
async def drug_menu_handler(message: Message, state: FSMContext):
    await state.set_state(States.DRUG_DATABASE_MENU)

    user_id = message.from_user.id

    # redis
    cache_key = f"user:{user_id}:allowed_drugs"
    cached_drugs_briefly = await redis.get(cache_key)

    if cached_drugs_briefly:
        # TODO: отправляем сообщение с клавиатурой (callback=)
        ...
    # TODO: получаем с ручки разрешенные препы с drug_name_ru и сохраняем в кэш
    else:
        ...


@router.callback_query(DrugDatabaseScrollingCallback.filter(), States.DRUG_DATABASE_MENU)
async def drug_menu_scrolling_handler(callback: CallbackQuery, callback_data: DrugDatabaseScrollingCallback):
    user_id = callback.from_user.id

    # redis
    cache_key = f"user:{user_id}:allowed_drugs"
    cached_drugs_briefly = await redis.get(cache_key)

    if cached_drugs_briefly:
        # TODO: отправляем сообщение с клавиатурой (callback=)
        ...
    # TODO: получаем с ручки разрешенные препы с drug_name_ru и сохраняем в кэш
    else:
        ...


# drug_describe key
@router.callback_query(DrugBrieflyCallback.filter(), States.DRUG_DATABASE_MENU)
async def drug_describe_briefly_handler(callback: CallbackQuery, callback_data: DrugBrieflyCallback, state: FSMContext):
    await state.set_state(States.DRUG_DATABASE_DESCRIBE)

    user_id = callback.from_user.id

    # callback data
    drug_id = callback_data.drug_id

    # redis
    cache_key = f"user:{user_id}:drug_describe:{drug_id}"
    cached_drugs_briefly = await redis.get(cache_key)

    if cached_drugs_briefly:
        # TODO: отправляем сообщение с описанием препарата и клавой (выбор описания)
        ...
    # TODO: получаем с ручки описание разрешенных препов и сохраняем в кэш
    else:
        ...


@router.callback_query(DrugDescribeCallback.filter(), States.DRUG_DATABASE_DESCRIBE)
async def drug_describe_handler(callback: CallbackQuery, callback_data: DrugDescribeCallback, state: FSMContext):
    user_id = callback.from_user.id

    # callback data
    describe_type = callback_data.describe_type  # тип описания (дозировки, пути, комбинации, исследования)
    drug_id = callback_data.drug_id

    # redis
    cache_key = f"user:{user_id}:drug_describe:{drug_id}"
    cached_drugs_briefly = await redis.get(cache_key)

    if cached_drugs_briefly:
        # TODO: отправляем сообщение с описанием препарата и клавой (выбор описания)
        ...
    # TODO: получаем с ручки краткое описание разрешенных препов и сохраняем в кэш
    else:
        ...
