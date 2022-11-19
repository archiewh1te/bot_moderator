from aiogram import Dispatcher

from .private_chat import IsPrivate
from .groups_chat import IsGroup
from .admin_chat import IsAdminCheck, IsAdminChat


# Функция которая выполняет установку кастомных фильтров
def setup(dp: Dispatcher):
    dp.filters_factory.bind(IsPrivate) # Устанавливаем кастомный фильтр на приватный чат с ботом
    dp.filters_factory.bind(IsGroup) # Устанавливаем кастомный фильтр Групп
    dp.filters_factory.bind(IsAdminCheck) # Устанавливаем фильтр на проверку Администратора из config
    dp.filters_factory.bind(IsAdminChat)  # Устанавливаем фильтр на проверку Администратора чата