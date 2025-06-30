import aiogram
from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import asyncio


bot = aiogram.Bot(token="6381941019:AAFi4pOscJjAHAoNnL45ezlYTlGqgOjJHEg")

dispatcher = Dispatcher()

start = aiogram.Router()


@start.message()
async def search_article(message: Message, state: FSMContext):
    drug_name = message.text  # Парацетамол
    await message.reply(text=drug_name)

dispatcher.include_router(start)


async def run_bot():
    await dispatcher.start_polling(bot)

while True:
    asyncio.run(run_bot())