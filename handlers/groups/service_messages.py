from aiogram import types

from filters import IsGroup
from loader import dp, bot
from utils.misc import rate_limit


@rate_limit(limit=0, key='groups')
@dp.message_handler(IsGroup(), content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def welcome_message(message: types.Message):
    # Получаем всех юзеров, которые подписались на наш чата
    members = ", ".join([mess.get_mention(as_html=True) for mess in message.new_chat_members])
    # Отправляем сообщение всем новым подписчикам бота
    await message.reply(f"Привет {members} 🤚")


@rate_limit(limit=0, key='groups')
@dp.message_handler(IsGroup(), content_types=types.ContentType.LEFT_CHAT_MEMBER)
async def left_chat_member(message: types.Message):
# Если пользователь вышел из чата сам
    if message.left_chat_member.id == message.from_user.id:
        await message.reply(f"👤{message.left_chat_member.get_mention(as_html=True)} вышел из чата.")
# Если пользователя кто-то выгнал
    else:
        await message.reply(f"👤{message.left_chat_member.get_mention(as_html=True)} был удалён из чата пользователем "
                             f"{message.from_user.get_mention(as_html=True)}.")