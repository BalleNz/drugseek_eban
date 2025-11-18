import logging

from aiogram import Router, flags
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, LinkPreviewOptions

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.bot.handlers.actions import drug_buy
from drug_search.bot.keyboards import drug_keyboard
from drug_search.bot.lexicon import MessageTemplates
from drug_search.bot.lexicon.enums import DrugMenu, ModeTypes
from drug_search.bot.lexicon.message_text import MessageText
from drug_search.bot.utils.format_message_text import DrugMessageFormatter
from drug_search.core.dependencies.bot.cache_service_dep import cache_service
from drug_search.core.lexicon import (
    ACTIONS_FROM_ASSISTANT, ARROW_TYPES, QUESTION_COST, MAX_MESSAGE_LENGTH_DEFAULT, SUBSCRIPTION_TYPES,
    MAX_MESSAGE_LENGTH_LITE, MAX_MESSAGE_LENGTH_PREMIUM
)
from drug_search.core.schemas import SelectActionResponse, DrugExistingResponse, UserSchema

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.message()
@flags.antispam(True)
async def main_action(
        message: Message,
        access_token: str,
        state: FSMContext,  # noqa
        api_client: DrugSearchAPIClient
):
    """Основная ручка для запросов юзера"""
    user: UserSchema = await cache_service.get_user_profile(access_token=access_token, telegram_id=message.from_user.id)

    if not user.allowed_tokens:
        await message.answer(MessageText.NO_TOKENS)
        return

    match user.subscription_type:
        case SUBSCRIPTION_TYPES.DEFAULT:
            if message.text.__len__() > MAX_MESSAGE_LENGTH_DEFAULT:
                await message.answer(MessageTemplates.MESSAGE_LENGTH_EXCEED.format(
                    subscription_info="без подписки",
                    max_message_len=MAX_MESSAGE_LENGTH_DEFAULT
                ))
                return
        case SUBSCRIPTION_TYPES.LITE:
            if message.text.__len__() > MAX_MESSAGE_LENGTH_LITE:
                await message.answer(MessageText.MESSAGE_LENGTH_EXCEED.format(
                    subscription_info="с лайт подпиской",
                    max_message_len=MAX_MESSAGE_LENGTH_LITE
                ))
                return
        case SUBSCRIPTION_TYPES.PREMIUM:
            if message.text.__len__() > MAX_MESSAGE_LENGTH_PREMIUM:
                await message.answer(MessageText.MESSAGE_LENGTH_EXCEED_PREMIUM)
                return

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
                    drug=drug_response.drug,
                    mode=ModeTypes.SEARCH,
                    drug_menu=DrugMenu.BRIEFLY,
                    user_subscribe_type=user.subscription_type,
                    user_query=message.text
                ),
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
        else:
            # [ предложить купить препарат ]
            logger.info(f"Препарат {drug_response.drug_name} есть в базе, юзер {user.telegram_id} пытается его купить")
            await drug_buy(
                message=message,
                is_message_from_user=True,
                api_client=api_client,
                access_token=access_token,
                drug_name=drug_response.drug_name,
                drug_id=drug_response.drug.id if drug_response.drug else None,
                danger_classification=drug_response.danger_classification,
                user=user
            )

    # [ определяем действие юзера ]
    else:
        message_request: Message = await message.answer(text=MessageText.QUERY_IN_PROCESS)

        action_response: SelectActionResponse = await api_client.assistant_get_action(
            access_token, message.text
        )

        logger.info(
            f"Действие юзера {user.telegram_id}: {action_response.action} {action_response.drug_menu if action_response.drug_menu else ""}")

        match action_response.action:
            case ACTIONS_FROM_ASSISTANT.QUESTION_DRUGS:
                # [ ответ на вопрос юзера с препаратами ]
                if user.allowed_tokens:
                    await message_request.edit_text(MessageText.ASSISTANT_WAITING)
                    await api_client.reduce_tokens(access_token, amount_tokens=QUESTION_COST)

                    await api_client.question_drugs_answer(  # via TaskService
                        access_token=access_token,
                        user_telegram_id=user.telegram_id,
                        question=message.text,
                        message_id=str(message_request.message_id),
                        arrow=ARROW_TYPES.FORWARD
                    )
                else:
                    await message_request.edit_text(
                        text=MessageText.NOT_ENOUGH_QUESTION_TOKENS
                    )

            case ACTIONS_FROM_ASSISTANT.QUESTION:
                # [ ответ на вопрос юзера ]
                if user.allowed_tokens:
                    await message_request.edit_text(MessageText.ASSISTANT_WAITING)
                    await api_client.reduce_tokens(access_token, amount_tokens=QUESTION_COST)

                    await api_client.question_answer(  # via TaskService
                        access_token=access_token,
                        user_telegram_id=user.telegram_id,
                        question=message.text,
                        message_id=str(message_request.message_id),
                    )
                else:
                    await message_request.edit_text(
                        text=MessageText.NOT_ENOUGH_QUESTION_TOKENS
                    )

            case ACTIONS_FROM_ASSISTANT.DRUG_MENU:
                # [ поиск препарата с конкретным разделом ]
                drug_existing_response: DrugExistingResponse | None = await api_client.search_drug(
                    action_response.drug_name,
                    access_token=access_token
                )

                logger.info(
                    f"Юзер {user.telegram_id} ищет раздел {action_response.drug_menu} препарата {drug_existing_response.drug_name}\n")
                logger.info(
                    f"Существует ли препарат: {drug_existing_response.is_exist}: {drug_existing_response.drug.id if drug_existing_response.drug else ""}")

                if drug_existing_response.is_allowed:
                    await message_request.edit_text(
                        text=DrugMessageFormatter.format_by_type(
                            drug_menu=action_response.drug_menu,
                            drug=drug_existing_response.drug
                        ),
                        reply_markup=drug_keyboard(
                            drug=drug_existing_response.drug,
                            mode=ModeTypes.SEARCH,
                            drug_menu=action_response.drug_menu,
                            user_subscribe_type=user.subscription_type,
                            user_query=message.text
                        ),
                        link_preview_options=LinkPreviewOptions(is_disabled=True)
                    )

                elif drug_existing_response.is_exist:
                    # [ предложить купить препарат ]
                    logger.info(f"Юзер {user.telegram_id} пытается купить {drug_existing_response.drug_name}")
                    logger.info(f"существует в базе: {drug_existing_response.is_drug_in_database}")
                    await drug_buy(
                        message=message_request,
                        api_client=api_client,
                        access_token=access_token,
                        drug_name=drug_existing_response.drug_name,
                        drug_id=drug_existing_response.drug.id if drug_existing_response.drug else None,
                        danger_classification=drug_existing_response.danger_classification,
                        user=user,
                        drug_menu=action_response.drug_menu
                    )
                else:
                    logger.error(f"Drug existing response error: {drug_existing_response}")
                    await message_request.edit_text(MessageText.ERROR_DRUG)

            case ACTIONS_FROM_ASSISTANT.DRUG_SEARCH:
                # [ поиск препарата ]
                drug_existing_response: DrugExistingResponse | None = await api_client.search_drug(
                    message.text,
                    access_token=access_token
                )
                if drug_existing_response.is_allowed:
                    message_text = DrugMessageFormatter.format_drug_briefly(drug_existing_response.drug)
                    await message_request.edit_text(
                        message_text,
                        reply_markup=drug_keyboard(
                            drug=drug_existing_response.drug,
                            drug_menu=DrugMenu.BRIEFLY,
                            user_subscribe_type=user.subscription_type,
                            mode=ModeTypes.SEARCH,
                            user_query=message.text
                        ),
                        link_preview_options=LinkPreviewOptions(is_disabled=True)
                    )
                elif drug_existing_response.is_exist:
                    # [ купить препарат ]
                    await drug_buy(
                        message=message_request,
                        api_client=api_client,
                        access_token=access_token,
                        drug_name=drug_existing_response.drug_name,
                        drug_id=drug_existing_response.drug.id if drug_response.drug else None,
                        danger_classification=drug_existing_response.danger_classification,
                        user=user
                    )
                else:
                    await message_request.edit_text(MessageText.DRUG_IS_NOT_EXIST)

            case ACTIONS_FROM_ASSISTANT.SPAM:
                # TODO возможно добавить
                await message_request.edit_text("Это сообщение распознано как спам")

            case ACTIONS_FROM_ASSISTANT.OTHER:
                await message_request.edit_text("Пожалуйста, уточните ваш запрос")
