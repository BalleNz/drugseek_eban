import logging
from uuid import UUID

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions

from drug_search.bot.keyboards import (DrugDescribeCallback, DrugListCallback,
                                       drug_database_keyboard, drug_list_keyboard,
                                       DescribeTypes, drug_keyboard)
from drug_search.bot.lexicon import MessageText
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.bot.lexicon.types import ModeTypes
from drug_search.core.schemas import DrugSchema, AllowedDrugsSchema, UserSchema
from drug_search.core.services.cache_service import CacheService

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.message(F.text == ButtonText.DRUG_DATABASE)
async def drug_menu_handler(
        message: Message,
        cache_service: CacheService,
        access_token: str,
        state: FSMContext,  # noqa
):
    """Отображает сообщение и позволяет листать препараты (после подтверждения)"""
    user_id = str(message.from_user.id)

    allowed_drugs_info: AllowedDrugsSchema = await cache_service.get_allowed_drugs(
        access_token=access_token,
        telegram_id=user_id
    )

    await message.answer(
        text=MessageText.format_drugs_info(allowed_drugs_info),
        reply_markup=drug_database_keyboard
    )


@router.callback_query(DrugListCallback.filter())
async def drug_list_handler(
        callback: CallbackQuery,
        cache_service: CacheService,
        access_token: str,
        callback_data: DrugListCallback,
):
    """Листинг препаратов"""
    user_id = str(callback.from_user.id)

    allowed_drugs_info: AllowedDrugsSchema = await cache_service.get_allowed_drugs(
        access_token=access_token,
        telegram_id=user_id
    )

    await callback.message.edit_text(
        text=MessageText.format_drugs_info(allowed_drugs_info),
        reply_markup=drug_list_keyboard(
            drugs=allowed_drugs_info.allowed_drugs,
            page=callback_data.page
        )
    )


@router.callback_query(DrugDescribeCallback.filter())
async def drug_describe_handler(
        callback: CallbackQuery,
        cache_service: CacheService,
        access_token: str,
        callback_data: DrugDescribeCallback,
        state: FSMContext  # noqa
):
    """
    Описание препарата в зависимости от Describe_type.
    Тут также передается page для плавного возвращения в меню
    """
    # callback data
    drug_id: UUID = callback_data.drug_id
    describe_type: DescribeTypes = callback_data.describe_type
    page: int = callback_data.page

    drug: DrugSchema = await cache_service.get_drug(
        access_token=access_token,
        drug_id=drug_id
    )
    user: UserSchema = await cache_service.get_user_profile(
        access_token=access_token,
        telegram_id=str(callback.from_user.id)
    )

    await callback.message.edit_text(
        text=MessageText.format_by_type(describe_type, drug),
        reply_markup=drug_keyboard(
            drug=drug,
            page=page,
            describe_type=describe_type,
            user_subscribe_type=user.subscription_type,
            mode=ModeTypes.DATABASE
        ),
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
