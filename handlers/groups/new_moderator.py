import asyncio
import datetime
import re

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import Message
from aiogram.utils.exceptions import BadRequest

from data import config
from filters import IsGroup, IsAdminCheck, IsAdminChat
from loader import dp, bot
from utils.db_api import moderator_commands
from utils.misc import rate_limit



@dp.message_handler(IsGroup(), Command('mute', prefixes='!'), IsAdminCheck(), IsAdminChat())
async def mute_chat_member(message: Message):
    if message.reply_to_message:
        member_id = message.reply_to_message.from_user.id
        chat_id = message.chat.id
        OnlyReadPermissions = types.ChatPermissions(can_send_messages=False,
                                                    can_send_media_messages=False,
                                                    can_send_polls=False,
                                                    can_send_other_messages=False,
                                                    can_add_web_page_previews=False,
                                                    can_change_info=False,
                                                    can_invite_users=False,
                                                    can_pin_messages=False)
        command = re.compile(r"(!mute) ?(\d+)? ?([a-zA-Zа-яА-Я ]+)?").match(message.text)
        time = command.group(2)
        comment = command.group(3)
        if not time:
            time = 30
        else:
            time = int(time)
        until_date = datetime.datetime.now() + datetime.timedelta(minutes=time)
        try:
            await bot.restrict_chat_member(chat_id=chat_id, user_id=member_id, permissions=OnlyReadPermissions, until_date=until_date)
            await message.reply(f'🔇 {message.reply_to_message.from_user.get_mention(as_html=True)} был ограничен отправлять сообщения на {time} минут.\n'
                                f'💬 Причина {comment}')
        except BadRequest:
            await message.reply(f'🚫 Этому пользователю нельзя ограничить возможность отправки сообщений!')
    else:
        msg = await message.reply(f'❌ Эта команда работает только в ответ на сообщение!')
        await asyncio.sleep(15)
        await msg.delete()


@dp.message_handler(IsGroup(), Command('unmute', prefixes='!'), IsAdminCheck(), IsAdminChat())
async def mute_chat_member(message: Message):
    if message.reply_to_message:
        member_id = message.reply_to_message.from_user.id
        chat_id = message.chat.id
        chat_permission = (await bot.get_chat(message.chat.id)).permissions
        try:
            await bot.restrict_chat_member(chat_id=chat_id, user_id=member_id, permissions=chat_permission, until_date=datetime.datetime.now())
            await message.reply(f'👤 {message.from_user.get_mention(as_html=True)} размутил на {message.reply_to_message.from_user.get_mention(as_html=True)}\n')
        except BadRequest:
            await message.reply('f🚫 Этого пользователя нельзя размутить!')
    else:
        msg = await message.reply(f'❌ Эта команда работает только в ответ на сообщение!')
        await asyncio.sleep(15)
        await msg.delete()


@rate_limit(limit=0, key='groups')
@dp.message_handler(IsGroup())
async def check_messages(message: types.Message):
    text = message.text
    await moderator_commands.check_chat_user(message)  # Проверяем если ли юзер в БД, если нету добавляем его

    if message.html_text == '/info':
        if message.reply_to_message is None:
            chatUser = await moderator_commands.select_chat_user(message.from_user.id)
            count_Violations = await moderator_commands.count_user_violations(message.from_user.id, hours=(24 * 30))
            await message.reply(f'📊 Статистика {message.from_user.get_mention(as_html=True)}\n'
                                f'👤 Репутация: {chatUser.reputation}\n'
                                f'🚑 Всего помощи: {chatUser.total_help}\n'
                                f'🔇 Кол-во мутов: {chatUser.mutes}\n'
                                f'🚫 Кол-во нарушений за последние 30 дней: {count_Violations}')
        else:
            chatUser = await moderator_commands.select_chat_user(message.reply_to_message.from_user.id)
            count_Violations = await moderator_commands.count_user_violations(message.reply_to_message.from_user.id, hours=(24 * 30))
            await message.reply(f'📊 Статистика {message.from_user.get_mention(as_html=True)}\n'
                                f'👤 Репутация: {chatUser.reputation}\n'
                                f'🚑 Всего помощи: {chatUser.total_help}\n'
                                f'🔇 Кол-во мутов: {chatUser.mutes}\n'
                                f'🚫 Кол-во нарушений за последние 30 дней: {count_Violations}')
    elif message.html_text == '+rep':
        if message.reply_to_message:
            if message.reply_to_message.from_user.id == message.from_user.id:
                await message.reply('🚫 Ты не можешь повысить репутацию сам себе.')
            else:
                chatUser = await moderator_commands.select_chat_user(message.from_user.id)
                rep_boost_user = await moderator_commands.select_chat_user(message.reply_to_message.from_user.id)
                if chatUser.last_rep_boost <= datetime.datetime.now() - datetime.timedelta(hours=0.5):
                    await moderator_commands.update_last_rep_boost(message.from_user.id)
                    await moderator_commands.add_reputation(message.reply_to_message.from_user.id)
                    await moderator_commands.add_chat_action(id=await moderator_commands.count_chat_action() +1,
                                                             user_id=message.from_user.id,
                                                             type='rep boost')
                    await message.reply(f'👤 {message.from_user.get_mention(as_html=True)} ({chatUser.reputation} репутации) поднял репутацию '
                                        f'{message.reply_to_message.from_user.get_mention(as_html=True)} ({rep_boost_user.reputation} + 1 репутации).')
                else:
                    await message.reply(f'🚫 Вы не можете поднимать репутацию еще {str(chatUser.last_rep_boost - datetime.datetime.now() + datetime.timedelta(hours=0.5)).split(".")[0]} часов.')

        else:
            msg = await message.reply(f'❌ Эта команда работает только в ответ на сообщение!')
            await asyncio.sleep(5)
            await msg.delete()


    elif message.html_text == '-rep':
        if message.reply_to_message:
            if message.reply_to_message.from_user.id == message.from_user.id:
                await message.reply('🚫 Ты не можешь понижать репутацию сам себе.')
            else:
                chatUser = await moderator_commands.select_chat_user(message.from_user.id)
                rep_boost_user = await moderator_commands.select_chat_user(message.reply_to_message.from_user.id)
                if chatUser.last_rep_boost <= datetime.datetime.now() - datetime.timedelta(hours=0.5):
                    await moderator_commands.update_last_rep_boost(message.from_user.id)
                    await moderator_commands.remove_reputation(message.reply_to_message.from_user.id)
                    await moderator_commands.add_chat_action(id=await moderator_commands.count_chat_action() +1,
                                                             user_id=message.from_user.id,
                                                             type='rep unboost')
                    await message.reply(f'👤 {message.from_user.get_mention(as_html=True)} ({chatUser.reputation} репутации) понизил репутацию '
                                        f'{message.reply_to_message.from_user.get_mention(as_html=True)} ({rep_boost_user.reputation} - 1 репутации).')

                else:
                    await message.reply(f'🚫 Вы не можете понижать репутацию еще {str(chatUser.last_rep_boost - datetime.datetime.now() + datetime.timedelta(hours=0.5)).split(".")[0]} часов.')

        else:
            msg = await message.reply(f'❌ Эта команда работает только в ответ на сообщение!')
            await asyncio.sleep(5)
            await msg.delete()


    # elif (await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)).status in [types.ChatMemberStatus.ADMINISTRATOR, types.ChatMemberStatus.CREATOR]:
    #     pass
    else:
        for entity in message.entities:
            if entity.type in ['url', 'text_link']:
                await message.delete()
                # Добавляем нарушение
                await moderator_commands.add_chat_action(id=await moderator_commands.count_chat_action() + 1,
                                                         user_id=message.from_user.id,
                                                         type='ads')
                await moderator_commands.check_violations(message) # Проверяем наличие нарушений
                break
        else:
            for banned_message in config.banned_messages:
                # Если в сообщении от пользователя есть запрещенное слово
                if banned_message.lower().replace(' ', '') in text.lower().replace(' ', ''):
                    await message.delete()
                    # Добавяем нарушение
                    await moderator_commands.add_chat_action(id=await moderator_commands.count_chat_action() + 1,
                                                             user_id=message.from_user.id,
                                                             type='bad word')
                    await moderator_commands.check_violations(message) # Проверяем наличие нарушений
                    break
            else:
                # Если кто-то сказал спасибо
                for words_of_gratitude in config.words_of_gratitude:
                    if words_of_gratitude.lower().replace(' ', '') in text.lower().replace(' ', ''):
                        if message.reply_to_message:
                            if message.reply_to_message.from_user.id == message.from_user.id:
                                await message.reply('👮‍♂ Даже не пытайся накрутить себе хорошую статистику')
                            else:
                                chatUser = await moderator_commands.select_chat_user(message.from_user.id)
                                if chatUser.last_help_boost <= datetime.datetime.now() - datetime.timedelta(hours=0.5):
                                    helping_user = await moderator_commands.select_chat_user(message.reply_to_message.from_user.id)
                                    chat_user = await moderator_commands.select_chat_user(message.from_user.id)
                                    await moderator_commands.add_total_help(helping_user.user_id)
                                    await moderator_commands.add_chat_action(id=await moderator_commands.count_chat_action() + 1,
                                                                             user_id=message.from_user.id,
                                                                             type='help boost')
                                    await moderator_commands.update_last_help_boost(message.from_user.id)
                                    await message.reply(f'👤 {message.reply_to_message.from_user.get_mention(as_html=True)} ({helping_user.total_help} помощи'
                                                        f'Помог {message.from_user.get_mention(as_html=True)} ({chat_user.total_help} помощи) и получается +1 помощь в свой рейтинг.')
                                else:
                                    await message.reply(f'🚫 Вы не можете сказать {words_of_gratitude} ещё {str(datetime.datetime.now() + datetime.timedelta(hours=0.5) - chatUser.last_help_boost).split(".")[0]}')


