import datetime
from aiogram import types
from asyncpg import UniqueViolationError
from data import config
from loader import bot
from utils.db_api.db_base import db
from utils.db_api.schemas.chat_actions import ChatAction
from utils.db_api.schemas.chat_user import ChatUser


# Добавяем пользователя из чата в БД
async def add_chat_user(user_id: int, first_name: str, last_name: str, user_name: str, status: str, reputation: int, total_help: int, mutes: int, last_rep_boost: datetime,  last_help_boost: datetime):
    try:
        chat_user = ChatUser(user_id=user_id, first_name=first_name, last_name=last_name, reputation=reputation, user_name=user_name, total_help=total_help, mutes=mutes,
                             last_rep_boost=last_rep_boost, last_help_boost=last_help_boost, status=status)
        await chat_user.create()
    except UniqueViolationError:
        print('Регистрация не создана')


# Проверяем есть ли юзер написавший сообщение в БД
async def check_chat_user(message):
    if message.reply_to_message:
        # Если не удалось получить юзера из БД
        if await select_chat_user(message.reply_to_message.from_user.id) is None:
            # Пытаемся его добавить
            await add_chat_user(user_id=message.reply_to_message.from_user.id,
                                first_name=message.reply_to_message.from_user.first_name,
                                last_name=message.reply_to_message.from_user.last_name,
                                user_name=message.reply_to_message.from_user.username,
                                status='active',
                                reputation=0,
                                total_help=0,
                                mutes=0,
                                last_rep_boost=datetime.datetime.now() - datetime.timedelta(hours=4),
                                last_help_boost=datetime.datetime.now() - datetime.timedelta(hours=4))

        else:
            pass
    else:
        # Если не удалось получить юезра из БД то добаавляем его
        if await select_chat_user(message.from_user.id) is None:
            await add_chat_user(user_id=message.from_user.id,
                                first_name=message.from_user.first_name,
                                last_name=message.from_user.last_name,
                                user_name=message.from_user.username,
                                status='active',
                                reputation=0,
                                total_help=0,
                                mutes=0,
                                last_rep_boost=datetime.datetime.now() - datetime.timedelta(hours=4),
                                last_help_boost=datetime.datetime.now() - datetime.timedelta(hours=4))
        else:
            pass


# Добавяем действие из чата в БД
async def add_chat_action(id: int, user_id: int, type: str):
    try:
        chat_action = ChatAction(id=id, user_id=user_id, type=type, added=datetime.datetime.now())
        await chat_action.create()
    except UniqueViolationError:
        print('Действие из чата не создано в БД')


# Количество нарушений юзера за последнее N-часов / Если 0 то за всё время
async def count_user_violations(user_id: int, hours: int = 0):
    violations = await ChatAction.query.where(ChatAction.user_id == user_id).gino.all() # Получаем все нарушения юзера
    if hours <= 0:
        # Число нарушений за всё время
        count = 0
        for violation in violations:
            if violation.type in ['ads', 'bad word']:
                count += 1
        return count
    else:
        count = 0
        # Число нарушений за последнее N-часов
        for violation in violations:
            # Проходимся по всем нарушениям юзера и считаем все которые были нарушены менее N-часов назад
            if violation.added >= datetime.datetime.now() - datetime.timedelta(hours=hours):
                count = 0
                for violation in violations:
                    if violation.type in ['ads', 'bad word']:
                        count += 1
        return count


async def check_violations(message):
    violations = await ChatAction.query.where(ChatAction.user_id == message.from_user.id).gino.all() # Получаем все нарушения от юзера
    count_bad_words = 0
    count_advertising = 0
    # Получаем каждое нарушение из списка
    for violation in violations:
        if violation.added >= datetime.datetime.now() - datetime.timedelta(minutes=config.time_of_violations):
            if violation.type == 'bad word': # Плохие слова
                count_bad_words +=1
            elif violation.type == 'ads': # Реклама
                count_advertising +=1
    OnlyReadPermissions = types.ChatPermissions(can_send_messages=False,
                                                can_send_media_messages=False,
                                                can_send_polls=False,
                                                can_send_other_messages=False,
                                                can_add_web_page_previews=False,
                                                can_change_info=False,
                                                can_invite_users=False,
                                                can_pin_messages=False)
    userChatActions = await ChatAction.query.where(ChatAction.user_id == message.from_user.id).gino.all()
    type = userChatActions[len(userChatActions) -1].type
    if type == 'bad word':
        if count_bad_words > 0: # Если количество плохих слов Больше 0
            if count_bad_words >= 5: # Если количество плохих слов больше или равно 5
                until_date = datetime.datetime.now() + datetime.timedelta(hours=config.mute_by_bad_word_time)
                await bot.restrict_chat_member(chat_id=message.chat_id,
                                               user_id=message.from_user.id,
                                               permissions=OnlyReadPermissions,
                                               until_date=until_date)
                return await message.answer(f'👤{message.from_user.get_mention(as_html=True)} был ограничен в возможности отправлять сообщения '
                                            f'на {config.mute_by_bad_word_time} часов.\n'
                                            f'📩Причина: Плохие слова в чате.')
            else:
                return await message.answer(f'🔍 Замечено плохое слово\n'
                                            f'👤 Его написал {message.from_user.get_mention(as_html=True)}\n'
                                            f'🤬 Предупреждение № {count_bad_words}\n')
    elif type == 'ads':
        if count_advertising > 0: # Если количество рекламных ссылок больше 0
            if count_advertising >= 3: # Если количество рекламных ссылок больше 3
                until_date = datetime.datetime.now() + datetime.timedelta(hours=config.mute_by_bad_word_time)
                await bot.restrict_chat_member(chat_id=message.chat_id,
                                               user_id=message.from_user.id,
                                               permissions=OnlyReadPermissions,
                                               until_date=until_date)
                return await message.answer(f'👤{message.from_user.get_mention(as_html=True)} был ограничен в возможности отправлять сообщения '
                                            f'на {config.mute_by_ads_time} часов.\n'
                                            f'📩Причина: Реклама в чате.')
            else:
                return await message.answer(f'🔍 Замечена реклама в чате\n'
                                            f'👤 Написал {message.from_user.get_mention(as_html=True)}\n'
                                            f'🤬 Предупреждение № {count_bad_words}\n')


# Функция обновляет дату последнего поднятия помощи
async def update_last_help_boost(user_id: int):
    chatUser = await ChatUser.query.where(ChatUser.user_id == user_id).gino.first()
    await chatUser.update(last_help_boost=datetime.datetime.now()).apply()


# Функция обновляет дату последнего поднятия или снятия репутации
async def update_last_rep_boost(user_id: int):
    chatUser = await ChatUser.query.where(ChatUser.user_id == user_id).gino.first()
    await chatUser.update(last_rep_boost=datetime.datetime.now()).apply()


# Чат событий
async def count_chat_action():
    count = await db.func.count(ChatAction.id).gino.scalar()
    return count


# Получаем чат юзера
async def select_chat_user(user_id: int):
    chat_user = await ChatUser.query.where(ChatUser.user_id == user_id).gino.first()
    return chat_user


# Функция добавляет рейтинг за помощь на +1
async def add_total_help(user_id: int):
    chat_user = await select_chat_user(user_id)
    await chat_user.update(total_help=chat_user.total_help + 1).apply()


# Функция которая добавляет репутацию +rep
async def add_reputation(user_id: int):
    chat_user = await select_chat_user(user_id)
    await chat_user.update(reputation=chat_user.reputation + 1).apply()


# Функция которая понижает репутацию -rep
async def remove_reputation(user_id: int):
    chat_user = await select_chat_user(user_id)
    await chat_user.update(reputation=chat_user.reputation - 1).apply()




# Функция которая добовляет количество мута в профиле
async def add_mutes(user_id: int):
    chat_user = await select_chat_user(user_id)
    await chat_user.update(mutes=chat_user.mutes + 1).apply()

