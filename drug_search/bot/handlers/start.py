import asyncio
import logging

from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.bot.keyboards.menu_markup import menu_keyboard
from keyboards.other_keyboards import open_referrals_menu_keyboard
from drug_search.bot.lexicon.message_text import MessageText
from drug_search.bot.utils.bot import send_delayed_message
from drug_search.core.utils.referrals_funcs import decode_referral_token

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.message(CommandStart())
async def start_dialog(
        message: Message,
        state: FSMContext,
        api_client: DrugSearchAPIClient,
        access_token: str,
        bot: Bot
):
    await state.clear()

    user_id = str(message.from_user.id)
    command_parts = message.text.split()

    # [ referrals check ]
    if len(command_parts) > 1 and command_parts[1].startswith('ref_'):
        token = command_parts[1][4:]  # skip: 'ref_'
        referrer_telegram_id = decode_referral_token(token)

        if referrer_telegram_id and referrer_telegram_id != user_id:
            logger.info(f"REFERRAL: User {user_id} came from {referrer_telegram_id} (token: {token})")

            try:
                await api_client.new_referral(
                    access_token=access_token,
                    referrer_telegram_id=referrer_telegram_id,
                    referral_telegram_id=user_id
                )
            except Exception as ex:
                logger.error(ex)
                pass

    await message.answer(text=MessageText.HELLO, reply_markup=menu_keyboard)
    logger.info(f"User {user_id} has started dialog.")

    # [ сообщение о рефералках ]
    asyncio.create_task(
        send_delayed_message(
            bot=bot,
            chat_id=message.chat.id,
            delay_minutes=5,
            text=MessageText.REFERRALS_INFO,
            reply_markup=open_referrals_menu_keyboard()
        )
    )

    # [ сообщение о режиме ]
    asyncio.create_task(
        send_delayed_message(
            bot=bot,
            chat_id=message.chat.id,
            delay_minutes=30,
            text=MessageText.SIMPLE_MODE_INFO
        )
    )

    # [ сообщение о бесплатных токенах ]
    asyncio.create_task(
        send_delayed_message(
            bot=bot,
            chat_id=message.chat.id,
            delay_minutes=15,
            text=MessageText.FREE_TOKENS_INFO
        )
    )
