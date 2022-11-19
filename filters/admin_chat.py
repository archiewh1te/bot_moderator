from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from data import config

from loader import bot


# настраиваемый фильтр для приватного чата с ботом (для Администраторов)
# Проверка айди в data.config и в БД
class IsAdminCheck(BoundFilter):
     async def check(self, message: types.Message) -> bool:
         if message.from_user.id in config.admins:
             return True
         else:
             await message.answer('⛔️Вы не Администратор! Данная команда не доступна⛔️')


class IsAdminChat(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        chat_member = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
        admin_types = [types.ChatMemberStatus.ADMINISTRATOR, types.ChatMemberStatus.CREATOR]
        return chat_member.status in admin_types

