import logging
from uuid import UUID

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions

from drug_search.bot.keyboards import drug_list_keyboard, drug_keyboard
from drug_search.bot.keyboards.callbacks import DrugDescribeResearchesCallback, DrugDescribeCallback, DrugListCallback
from drug_search.bot.keyboards.drug_keyboards import drug_researches_keyboard
from drug_search.bot.keyboards.other_keyboards import get_subscription_packages_from_limitable_keyboard
from drug_search.bot.lexicon.enums import ModeTypes
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.bot.lexicon.message_text import MessageText
from drug_search.bot.utils.format_message_text import DrugMessageFormatter
from drug_search.core.lexicon.enums import DrugMenu, SUBSCRIPTION_TYPES
from drug_search.core.schemas import DrugSchema, UserSchema, AllowedDrugsInfoSchema
from drug_search.core.services.cache_logic.cache_service import CacheService

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.message(F.text == ButtonText.DRUG_DATABASE)
async def drug_menu_handler(
        message: Message,
        cache_service: CacheService,
        access_token: str,
        state: FSMContext,  # noqa
):
    """Отображает первую страницу препаратов"""
    user_id = str(message.from_user.id)

    allowed_drugs_info: AllowedDrugsInfoSchema = await cache_service.get_allowed_drugs(
        access_token=access_token,
        telegram_id=user_id
    )

    await message.answer(
        text=MessageText.formatters.DRUGS_INFO(allowed_drugs_info=allowed_drugs_info),
        reply_markup=drug_list_keyboard(
            drugs=allowed_drugs_info.allowed_drugs,
            page=0
        )
    )


@router.callback_query(DrugListCallback.filter())
async def drug_list_handler(
        callback: CallbackQuery,
        cache_service: CacheService,
        access_token: str,
        callback_data: DrugListCallback,
):
    """Листинг препаратов (стрелочки)"""
    await callback.answer()

    user_id = str(callback.from_user.id)

    allowed_drugs_info: AllowedDrugsInfoSchema = await cache_service.get_allowed_drugs(
        access_token=access_token,
        telegram_id=user_id
    )

    await callback.message.edit_text(
        text=MessageText.formatters.DRUGS_INFO(allowed_drugs_info=allowed_drugs_info),
        reply_markup=drug_list_keyboard(
            drugs=allowed_drugs_info.allowed_drugs,
            page=callback_data.page
        )
    )


@router.callback_query(DrugDescribeResearchesCallback.filter())
async def drug_describe_researches_handler(
        callback: CallbackQuery,
        cache_service: CacheService,
        access_token: str,
        callback_data: DrugDescribeResearchesCallback,
        state: FSMContext  # noqa
):
    """меню с исследованиями со стрелками"""
    await callback.answer()

    # [ cache ]
    user: UserSchema = await cache_service.get_user_profile(
        access_token,
        str(callback.from_user.id)
    )

    # [ callback data ]
    drug_id: UUID = callback_data.drug_id
    research_number: int = callback_data.research_number
    current_page_number: int = callback_data.current_page_number or 0

    if user.subscription_type in (SUBSCRIPTION_TYPES.DEFAULT, SUBSCRIPTION_TYPES.LITE):
        """Проверка на подписку для раздела исследований"""
        await callback.message.edit_text(
            text=MessageText.RESEARCHES_LIMITATION,
            reply_markup=get_subscription_packages_from_limitable_keyboard(
                user_subscription_type=SUBSCRIPTION_TYPES.LITE,
                drug_id=drug_id,
            ),
            LinkPreviewOptions=LinkPreviewOptions(is_disabled=True)
        )
    else:
        drug: DrugSchema = await cache_service.get_drug(
            access_token=access_token,
            drug_id=drug_id
        )

        await callback.message.edit_text(
            text=DrugMessageFormatter.format_researches(drug, research_number),
            reply_markup=drug_researches_keyboard(
                researches=drug.researches,
                drug_id=drug_id,
                research_number=research_number,
                current_page_number=current_page_number
            ),
            link_preview_options=LinkPreviewOptions(is_disabled=True)
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
    await callback.answer()

    user: UserSchema = await cache_service.get_user_profile(
        access_token=access_token,
        telegram_id=str(callback.from_user.id)
    )

    # [ callback data ]
    drug_id: UUID = callback_data.drug_id
    describe_type: DrugMenu = callback_data.drug_menu
    page: int = callback_data.page

    if callback_data.drug_menu == DrugMenu.MECHANISM and user.subscription_type in (
    SUBSCRIPTION_TYPES.DEFAULT, SUBSCRIPTION_TYPES.LITE):
        """Проверка на подписку для раздела механизма действия"""
        await callback.message.edit_text(
            text=MessageText.MECHANISM_LIMITATION,
            reply_markup=get_subscription_packages_from_limitable_keyboard(
                user_subscription_type=user.subscription_type,
                drug_id=drug_id,
            ),
            LinkPreviewOptions=LinkPreviewOptions(is_disabled=True)
        )
    else:
        drug: DrugSchema = await cache_service.get_drug(
            access_token=access_token,
            drug_id=drug_id
        )

        await callback.message.edit_text(
            text=MessageText.formatters.DRUG_BY_TYPE(drug_menu=describe_type, drug=drug),
            reply_markup=drug_keyboard(
                drug=drug,
                page=page,
                drug_menu=describe_type,
                user_subscribe_type=user.subscription_type,
                mode=ModeTypes.DATABASE
            ),
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
