from aiogram import types

from filters import IsPrivate
from loader import dp

from utils.misc import rate_limit


# Функция по команде /start
@rate_limit(limit=3)
@dp.message_handler(IsPrivate(), text='/start')
async def command_start(message: types.Message):
    await message.answer(f"Привет {message.from_user.get_mention(as_html=True)} 🤚")



