"""
HOW TO USE  DI INJECTION.
"""
from aiogram.types import Message

from core.services.drug import DrugService


# @dp.message_handler(commands=["get_drug"])
async def handle_get_drug(message: Message, service: DrugService = None):
    drug = await service.get_drug(message.text)
    await message.answer(str(drug))
