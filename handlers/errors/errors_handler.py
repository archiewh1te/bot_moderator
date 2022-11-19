import logging

from aiogram.utils.exceptions import (Unauthorized,MessageCantBeDeleted, MessageToDeleteNotFound, MessageNotModified,
                                      MessageTextIsEmpty, CantParseEntities, CantDemoteChatCreator, InvalidQueryID,
                                      RetryAfter, TelegramAPIError, BadRequest)

from loader import dp


@dp.errors_handler()
async def errors_handler(update, exception):

    if isinstance(exception, Unauthorized):
        logging.info(f'Неавторизованный {exception}')
        return True    # Неавторизованный

    if isinstance(exception, MessageCantBeDeleted):
        logging.info('Сообщение не может быть удалено')
        return True   # Сообщение не может быть удалено

    if isinstance(exception, MessageToDeleteNotFound):
        logging.info('Сообщение для удаления не найдено')
        return True   # Сообщение для удаления не найдено

    if isinstance(exception, MessageNotModified):
        logging.info('Сообщение не изменено')
        return True   # Сообщение не изменено

    if isinstance(exception, MessageTextIsEmpty):
        logging.debug('Текст сообщения пуст')
        return True   # Текст сообщения пуст

    if isinstance(exception, CantParseEntities):
        logging.debug(f'Не удается разобрать объекты. ExceptionArgs: {exception.args}')
        return True   # Не удается разобрать объекты

    if isinstance(exception, CantDemoteChatCreator):
        logging.debug('Не возможно понизить создателя чата')
        return True   # Невозможно понизить создателя чата

    if isinstance(exception, InvalidQueryID):
        logging.exception(f'Недопустимый идентификатор запроса: {exception} \nUpdate: {update}')
        return True   # Недопустимый идентификатор запроса

    if isinstance(exception, RetryAfter):
        logging.exception(f'Повторить после: {exception} \nUpdate: {update}')
        return True   # Повторить после

    if isinstance(exception, BadRequest):
        logging.exception(f'Неверный запрос: {exception} \nUpdate: {update}')
        return True   # Неверный запрос

    if isinstance(exception, TelegramAPIError):
        logging.exception(f'Ошибка API Telegram: {exception} \nUpdate: {update}')
        return True   # Ошибка API Telegram

    # Другая ошибка
    logging.exception(f'Update: {update} \nException: {exception}')
