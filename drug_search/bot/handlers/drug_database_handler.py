import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage import redis
from aiogram.types import Message

from lexicon.keyboard_words import ButtonText

router = Router(name=__name__)
logger = logging.getLogger(name=__name__)


@router.message(F.text == ButtonText.DRUG_DATABASE)
async def drug_menu_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id

    cache_key = f"user:{user_id}:drugs_briefly"
    cached_drugs_briefly = await redis.get(cache_key)

    
