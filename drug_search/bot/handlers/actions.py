import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, LinkPreviewOptions, CallbackQuery

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.bot.keyboards import DescribeTypes, drug_keyboard, WrongDrugFoundedCallback, \
    buy_request_keyboard
from drug_search.bot.utils.format_message_text import DrugMessageFormatter
from drug_search.core.dependencies.cache_service_dep import cache_service
from drug_search.core.lexicon.enums import ACTIONS_FROM_ASSISTANT
from drug_search.core.schemas import (SelectActionResponse,
                                      DrugExistingResponse, UserSchema)
from lexicon import MessageTemplates

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.callback_query(WrongDrugFoundedCallback.filter())
async def wrong_drug_founded(
        callback_query: CallbackQuery,
        access_token: str,
        state: FSMContext,  # noqa
        callback_data: WrongDrugFoundedCallback,
        api_client: DrugSearchAPIClient
):
    user: UserSchema = await cache_service.get_user_profile(access_token, callback_query.from_user.id)
    await callback_query.message.edit_text(MessageTemplates.DRUG_MANUAL_SEARCHING)

    drug_response: DrugExistingResponse = await api_client.search_drug_without_trigrams(callback_data.drug_name_query, access_token)
    if drug_response.is_exist:
        if drug_response.is_allowed:
            message_text: str = DrugMessageFormatter.format_drug_briefly(drug_response.drug)
            await callback_query.message.edit_text(
                message_text,
                reply_markup=drug_keyboard(
                    drug_id=drug_response.drug.id,
                    describe_type=DescribeTypes.BRIEFLY,
                    user_subscribe_type=user.subscription_type,
                    drug_name=drug_response.drug.name,
                    drug_last_update=drug_response.drug.updated_at
                ),
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
        else:
            # [ предложить купить препарат ]
            await callback_query.message.edit_text(
                text=MessageTemplates.DRUG_BUY_REQUEST.format(
                    drug_name_ru=drug_response.drug_name_ru
                ),
                reply_markup=buy_request_keyboard(
                    drug_id=drug_response.drug.id if drug_response.drug else None,
                    drug_name=drug_response.drug_name,
                    danger_classification=drug_response.danger_classification
                ),
            )
    else:
        await callback_query.message.edit_text(MessageTemplates.DRUG_IS_NOT_EXIST)


@router.message()
async def main_action(
        message: Message,
        access_token: str,
        state: FSMContext,  # noqa
        api_client: DrugSearchAPIClient
):
    """Основная ручка для запросов юзера"""

    user: UserSchema = await cache_service.get_user_profile(access_token=access_token, telegram_id=message.from_user.id)

    # [ search ONLY with trigrams ]
    drug_response: DrugExistingResponse = await api_client.search_drug_trigrams(
        drug_name_query=message.text,
        access_token=access_token
    )

    if drug_response.is_exist:
        if drug_response.is_allowed:
            message_text = DrugMessageFormatter.format_drug_briefly(drug_response.drug)
            await message.answer(
                message_text,
                reply_markup=drug_keyboard(
                    drug_id=drug_response.drug.id,
                    describe_type=DescribeTypes.BRIEFLY,
                    user_subscribe_type=user.subscription_type,
                    drug_name=message.text,
                    drug_last_update=drug_response.drug.updated_at
                ),
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
        else:
            # [ предложить купить препарат ]
            await drug_response.edit_text(
                text=MessageTemplates.DRUG_BUY_REQUEST.format(
                    drug_name_ru=drug_response.drug_name_ru
                ),
                reply_markup=buy_request_keyboard(
                    drug_id=drug_response.drug.id if drug_response.drug else None,
                    drug_name=drug_response.drug_name,
                    danger_classification=drug_response.danger_classification
                ),
            )

    # [ определяем действие юзера ]
    else:
        message_request: Message = await message.answer(text=MessageTemplates.QUERY_IN_PROCESS)

        action_response: SelectActionResponse = await api_client.assistant_get_action(
            access_token, message.text
        )

        match action_response.action:
            case ACTIONS_FROM_ASSISTANT.QUESTION:
                # [ ответ на вопрос юзера ]

                if user.allowed_question_requests:
                    await message_request.edit_text(MessageTemplates.ASSISTANT_WAITING)
                    await api_client.reduce_tokens(access_token, amount_question_tokens=1)

                    await api_client.action_answer(  # via TaskService
                        access_token=access_token,
                        user_telegram_id=user.telegram_id,
                        question=message.text,
                        old_message_id=str(message_request.message_id)
                    )
                else:
                    await message_request.edit_text(
                        text=MessageTemplates.NOT_ENOUGH_QUESTION_TOKENS
                    )

            case ACTIONS_FROM_ASSISTANT.DRUG_MENU:
                # [ поиск препарата с конкретным разделом ]

                drug_existing_response: DrugExistingResponse | None = await api_client.search_drug(
                    action_response.drug_name,
                    access_token=access_token
                )

                if drug_existing_response.is_allowed:
                    await message_request.edit_text(
                        text=DrugMessageFormatter.format_by_type(
                            describe_type=DescribeTypes(action_response.drug_menu),
                            drug=drug_existing_response.drug
                        ),
                        reply_markup=drug_keyboard(
                            drug_id=drug_existing_response.drug.id,
                            describe_type=DescribeTypes(action_response.drug_menu),
                            user_subscribe_type=user.subscription_type,
                            drug_name=drug_existing_response.drug.name,
                            drug_last_update=drug_response.drug.updated_at
                        ),
                        link_preview_options=LinkPreviewOptions(is_disabled=True)
                    )

                elif drug_existing_response.is_exist:
                    # [ предложить купить препарат ]
                    await message_request.edit_text(
                        text=MessageTemplates.DRUG_BUY_REQUEST.format(
                            drug_name_ru=action_response.drug_name
                        ),
                        reply_markup=buy_request_keyboard(
                            drug_id=drug_existing_response.drug.id if drug_existing_response.drug else None,
                            drug_name=message.text,
                            danger_classification=drug_existing_response.danger_classification
                        ),
                    )
                else:
                    logger.error(f"Drug existing response error: {drug_existing_response}")
                    await message_request.edit_text(MessageTemplates.ERROR_DRUG)

            case ACTIONS_FROM_ASSISTANT.DRUG_SEARCH:
                # [ поиск препарата ]
                drug_existing_response: DrugExistingResponse | None = await api_client.search_drug(
                    message.text,
                    access_token=access_token
                )
                if drug_existing_response.is_allowed:
                    message_text = DrugMessageFormatter.format_drug_briefly(drug_existing_response.drug)
                    await message.answer(
                        message_text,
                        reply_markup=drug_keyboard(
                                drug_id=drug_existing_response.drug.id,
                                describe_type=DescribeTypes.BRIEFLY,
                                user_subscribe_type=user.subscription_type,
                                drug_last_update=drug_response.drug.updated_at
                            ),
                        link_preview_options=LinkPreviewOptions(is_disabled=True)
                    )
                elif drug_existing_response.is_exist:
                    # [ купить препарат ]
                    await message_request.edit_text(
                        text=MessageTemplates.DRUG_BUY_REQUEST.format(
                            drug_name_ru=drug_existing_response.drug_name_ru
                        ),
                        reply_markup=buy_request_keyboard(
                            drug_id=drug_existing_response.drug.id if drug_existing_response.drug else None,
                            drug_name=message.text,
                            danger_classification=drug_existing_response.danger_classification
                        ),
                    )
                else:
                    await message.answer(MessageTemplates.DRUG_IS_NOT_EXIST)

            case ACTIONS_FROM_ASSISTANT.SPAM:
                # TODO возможно добавить
                await message.answer("Это сообщение распознано как спам")

            case ACTIONS_FROM_ASSISTANT.OTHER:
                await message.answer("Пожалуйста, уточните ваш запрос")
