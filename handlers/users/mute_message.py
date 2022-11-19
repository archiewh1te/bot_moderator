from aiogram import types

from filters import IsPrivate
from loader import dp, Dispatcher


# Пустой хендлер echo регаирует на любое сообщение
@dp.message_handler(IsPrivate())
async def send_message(message: types.Message):
        await message.answer(f'Бот не видит что вы пишите')



