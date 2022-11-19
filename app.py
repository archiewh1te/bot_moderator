async def on_startup(dp):

    # Подключение мидлвар и фильтр
    import middlewares
    middlewares.setup(dp)

    import filters
    filters.setup(dp)


    # Подключение БД
    from loader import db
    from utils.db_api.db_base import on_startup
    print('Подключение к PostgreSQL')
    await on_startup(dp)


    # Удаление БД
    # print('Удаление Базы Данных')
    # await db.gino.drop_all()


    # Создание таблиц
    print('Создание таблиц')
    await db.gino.create_all()


    # Подключение уведомление админам о запуске
    from utils.notify_admins import on_startup_notify
    await on_startup_notify(dp)


    # Подключение команд бота
    from utils.set_bot_commands import set_default_commands
    await set_default_commands(dp)
    print('Бот запущен')


if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp


    executor.start_polling(dp, on_startup=on_startup, skip_updates=False)
