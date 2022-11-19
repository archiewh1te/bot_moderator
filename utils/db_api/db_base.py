from gino import Gino

import sqlalchemy as sa
from typing import List
import datetime
from aiogram import Dispatcher

from sqlalchemy import Column, BigInteger, String, DateTime

from data import config

from data.config import admins
import logging


db = Gino()


class BaseModel(db.Model):
    __abstract__ = True

    def __str__(self):
        model = self.__class__.__name__
        table: sa.Table = sa.inspect(self.__class__)
        primary_key_columns: List[sa.Column] = table.primary_key.columns
        values = {
            column.name: getattr(self, self._column_name_map[column.name])
            for column in primary_key_columns
        }
        values_str = " ".join(f"{name}={value!r}" for name, value in values.items())
        return f"<{model} {values_str}>"



class TimedBaseModel(BaseModel):
    __abstract__ = True

    created_at = Column(DateTime, server_default=db.func.now())
    updated_at = Column(DateTime,
                        default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow,
                        server_default=db.func.now())


async def on_startup(dp: Dispatcher):
    await db.set_bind(config.POSTGRES_URI)
    print('Установка связи с PostgreSQL')
    for admin in admins:
        try:
            text = ('Установка связи с PostgreSQL')
            await dp.bot.send_message(chat_id=admin, text=text)
        except Exception as err:
            logging.exception(err)