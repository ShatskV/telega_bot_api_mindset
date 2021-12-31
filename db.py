import settings
from datetime import datetime
import enum
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
engine = create_engine(settings.SQLALCHEMY_URI)
db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


class Settings(enum.Enum):
    instagram = 'instagram'
    list_tags = 'list'


class Action(enum.Enum):
    desc_tags = 'iu_decs_and_tags'
    desc = 'iu_decs'
    tags = 'iu_tags'


class TgUser(Base):
    __tablename__ = 'tg_users'
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, index=True)
    tg_user_name  = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    lang = Column(String(4))
    tags_format = Column(Enum(Settings), default=Settings.instagram)
    free_act = Column(Integer())
    create_at = Column(DateTime(timezone=False), default=datetime.utcnow())
    bot_feedback = Column(String(10000))
    is_banned = Column(Boolean, default=False)

    def __repr__(self):
        return f'<Telegram_user {self.id}>'
    

class TgAction(Base):
    __tablename__ = 'tg_actions'
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(Integer, ForeignKey(TgUser.tg_user_id))
    # tg_msg_id = Column(Integer)
    action_type = Column(Enum(Action))
    image_uuid = Column(String(50), index=True)
    image_name = Column(String)
    lang = Column(String(4))
    image_type = Column(String())
    image_size = Column(Integer)
    create_at = Column(DateTime(timezone=False), default=datetime.utcnow())
    responce = Column(String(20000))

    def __repr__(self):
        return f'<Telegram_user_action {self.telegram_user_id} {self.action}>'


class TgChatHistory(Base):
    __tablename__ = 'tg_chat_history'
    id = Column(Integer)
    tg_msg_id = Column(Integer)
    tg_user_id = Column(Integer, index=True)
    user_msg = Column(String(10000))
    bot_msg = Column(String(10000))


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
