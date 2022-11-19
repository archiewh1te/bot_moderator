from utils.db_api.db_base import BaseModel

from sqlalchemy import Column, BigInteger, String, sql, DateTime


class ChatAction(BaseModel):
    __tablename__ = 'chat_actions'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger)
    type = Column(String(50))
    added = Column(DateTime)

    query:sql.select