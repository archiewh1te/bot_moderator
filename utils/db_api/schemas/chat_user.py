from utils.db_api.db_base import TimedBaseModel

from sqlalchemy import Column, BigInteger, String, sql, DateTime


# Создание таблицы юзеров из чата
class ChatUser(TimedBaseModel):
    __tablename__ = 'chat_users'
    user_id = Column(BigInteger, primary_key=True)
    first_name = Column(String(200))
    last_name = Column(String(200))
    user_name = Column(String(100))
    reputation = Column(BigInteger)
    total_help = Column(BigInteger)
    mutes = Column(BigInteger)
    last_rep_boost = Column(DateTime)
    last_help_boost = Column(DateTime)
    status = Column(String(30))

    query: sql.select