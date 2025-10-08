import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, LinkPreviewOptions, CallbackQuery

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.bot.keyboards import DescribeTypes, drug_describe_types_keyboard
from drug_search.bot.utils.format_message_text import DrugMessageFormatter
from drug_search.core.dependencies.cache_service_dep import cache_service
from drug_search.core.lexicon.enums import ACTIONS_FROM_ASSISTANT
from drug_search.core.schemas import (SelectActionResponse,
                                      DrugExistingResponse, UserSchema)
from keyboards import WrongDrugFoundedCallback

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.message(WrongDrugFoundedCallback.filter())
async def wrong_drug_founded(
        callback_query: CallbackQuery,
        access_token: str,
        state: FSMContext,
        callback_data: WrongDrugFoundedCallback,
        api_client: DrugSearchAPIClient
):
    user: UserSchema = await cache_service.get_user_profile(access_token, callback_query.from_user.id)
    message: Message = await callback_query.message.answer("Поиск препарата..")

    drug_response: DrugExistingResponse = await api_client.search_drug(callback_data.drug_name_query, access_token)
    await message.edit_text(
        text=DrugMessageFormatter.format_drug_briefly(drug_response.drug),
        callback_data=drug_describe_types_keyboard(
            drug_id=drug_response.drug.id,
            describe_type=DescribeTypes.BRIEFLY,
            user_subscribe_type=user.subscription_type,
        )
    )


@router.message()
async def main_action(
        message: Message,
        access_token: str,
        state: FSMContext,
        api_client: DrugSearchAPIClient
):
    """Основная ручка для запросов юзера"""

    user: UserSchema = await cache_service.get_user_profile(access_token=access_token, telegram_id=message.from_user.id)

    # Fast drug search ONLY with trigrams
    drug_response: DrugExistingResponse = await api_client.search_drug_trigrams(
        drug_name_query=message.text,
        access_token=access_token
    )

    if drug_response.is_drug_in_database:
        message_text = DrugMessageFormatter.format_drug_briefly(drug_response.drug)
        await message.answer(
            message_text,
            reply_markup=drug_describe_types_keyboard(
                drug_id=drug_response.drug.id,
                describe_type=DescribeTypes.BRIEFLY,
                user_subscribe_type=user.subscription_type,
                drug_name=message.text
            ),
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
    else:
        message_request: Message = await message.answer(text="Запрос принят.. обрабатываю")

        action_response: SelectActionResponse = await api_client.assistant_get_action(
            access_token, message.text
        )

        match action_response.action:
            case ACTIONS_FROM_ASSISTANT.QUESTION:
                # TODO: делает задачу в TaskService (вот эту всю хуйню туда запихать просто)
                if user.allowed_question_requests:
                    # отнимаем токен
                    await api_client.add_tokens(access_token, amount_question_tokens=-1)
                    # сразу инвалидируем кеш (для актуальности количества токенов)
                    await cache_service.redis_service.invalidate_user_data(message.from_user.id)

                    await api_client.action_answer(
                        access_token=access_token,
                        user_telegram_id=user.telegram_id,
                        question=message.text,
                        old_message_id=str(message_request.message_id)
                    )


            case ACTIONS_FROM_ASSISTANT.DRUG_SEARCH:
                drug_existing_response: DrugExistingResponse | None = await api_client.search_drug(
                    message.text,
                    access_token=access_token
                )

                if drug_existing_response.is_exist:
                    if drug_existing_response.is_drug_in_database:
                        message_text = DrugMessageFormatter.format_drug_briefly(drug_existing_response.drug)
                        await message.answer(
                            message_text,
                            reply_markup=drug_describe_types_keyboard(
                                drug_id=drug_existing_response.drug.id,
                                describe_type=DescribeTypes.BRIEFLY,
                                user_subscribe_type=user.subscription_type
                            ),
                            link_preview_options=LinkPreviewOptions(is_disabled=True)
                        )
                    else:
                        await message.answer("такого препарат нет в БД ")

            case ACTIONS_FROM_ASSISTANT.SPAM:
                await message.answer("Это сообщение распознано как спам")

            case ACTIONS_FROM_ASSISTANT.OTHER:
                await message.answer("Пожалуйста, уточните ваш запрос")
