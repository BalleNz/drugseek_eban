import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from drug_search.bot.keyboards import (DrugDescribeCallback, DrugListCallback,
                                       drug_database_list_keyboard, get_drugs_list_keyboard,
                                       get_drug_describe_menu_keyboard)
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.bot.states.states import States
from drug_search.core.schemas import DrugSchema, AllowedDrugsSchema
from drug_search.core.services.redis_service import RedisService

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.message(F.text == ButtonText.DRUG_DATABASE)
async def drug_menu_handler(
        message: Message,
        redis_service: RedisService,
        access_token: str,
        state: FSMContext,
):
    await state.set_state(States.DRUG_DATABASE_MENU)

    user_id = str(message.from_user.id)

    allowed_drugs_info: AllowedDrugsSchema = await redis_service.get_allowed_drugs(
        access_token=access_token,
        telegram_id=user_id
    )

    # TODO: сообщение со статистикой + клавиатура drug_database_get_full_list
    await message.answer(
        text=...,
        reply_markup=drug_database_list_keyboard
    )


@router.callback_query(DrugListCallback.filter(), States.DRUG_DATABASE_MENU)
async def drug_list_handler(
        callback: CallbackQuery,
        redis_service: RedisService,
        access_token: str,
        callback_data: DrugListCallback,
):
    user_id = str(callback.from_user.id)

    allowed_drugs_info: AllowedDrugsSchema = await redis_service.get_allowed_drugs(
        access_token=access_token,
        telegram_id=user_id
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
        access_token: str,
        callback_data: DrugDescribeCallback,
        state: FSMContext
):
    await state.set_state(States.DRUG_DATABASE_DESCRIBE)

    user_id = str(callback.from_user.id)

    # callback data
    drug_id = callback_data.drug_id

    drug_description: DrugSchema = await redis_service.get_drug(
        access_token=access_token,
        telegram_id=user_id,
        drug_id=drug_id
    )

    # TODO: отправляем сообщение с описанием препарата и клавой (выбор описания)
    await callback.message.edit_text(
        text=...,
        reply_markup=get_drug_describe_menu_keyboard(
            drug_id=drug_id
        )
    )
