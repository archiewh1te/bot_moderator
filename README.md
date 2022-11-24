**Moderator_Bot v1.0**

**Author:** @ArchieWh1te

**Language:** Python 3.8

**framework for Telegram** Aiogram 2.23.1 

**License:** Free

[![PyPI](https://img.shields.io/pypi/v/aiogram?label=aiogram&logo=telegram&logoColor=aiogram)](https://pypi.org/project/aiogram/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aiogram?color=green&logo=python&logoColor=green)

### Бот модератор в группе / чате
**Запуск бота**

Для запуска бота используйте файл *app.py*

**Команды:**

**/info** - статистика пользователя

**!unmute / !mute время в минутах** - Команда для Администратора Снять и поставить мут

**Для работы вам потребуется:**

1)установить все зависимости из *requirements.txt*

2)Установить **PostgreSQL** и настроить его 

3)Отредактировать файл **.env** там указываете конфигурацию для подключения к **PostgreSQL**

4)Изменить настройки в файле **config** на свои параметры в переменной *admins*

**Скриншоты**

*Когда пользователь зашел в группу или его добавили*

![adduser](screens/adduser.png)

*Когда пользователя удалили*

![deluser](screens/delname.png)

*Статистика*

![info](screens/info.png)

*Дать мут*

![mute](screens/mute.png)

*Снять мут*

![unmute](screens/unmute.png)

*Удаление рекламных ссылок*

![reklama](screens/reklama.png)

*Удаление плохих слов*

![mat](screens/mat.png)
