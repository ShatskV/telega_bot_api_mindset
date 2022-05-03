"""DB models."""
import asyncio
from email.policy import default
import enum

from sqlalchemy import (BIGINT, Boolean, Column, DateTime, Integer, MetaData,
                        String)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime

from config import settings

engine = create_async_engine(settings.SQLALCHEMY_URI)
async_session = sessionmaker(bind=engine,  expire_on_commit=False, class_=AsyncSession)

metadata = MetaData(schema='bot')
Base = declarative_base(metadata=metadata)


class MyEnumMeta(enum.EnumMeta):
    def __contains__(cls, item):
        return item in [v.value for v in cls.__members__.values()]


class TagFormat(enum.Enum, metaclass=MyEnumMeta):
    instagram = 'instagram'
    list_tags = 'list'


class Action(enum.Enum, metaclass=MyEnumMeta):
    desc_tags = 'iu_decs_and_tags'
    desc = 'iu_decs'
    tags = 'iu_tags'


class YandexAction(enum.Enum):
    check = 'check_token'
    upload = 'upload_file'


class TypeUpdate(enum.Enum):
    message = 'message'
    callback = 'callback'


class TgUser(Base):
    __tablename__ = 'tg_users'

    id = Column(Integer, primary_key=True)
    tg_user_id = Column(Integer, nullable=False, index=True, unique=True)
    user_id = Column(Integer, index=True)
    tg_user_name = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    lang = Column(String(4), default='en')
    tags_format = Column(ENUM(TagFormat), default=TagFormat.instagram)
    rating = Column(Boolean(), default=True)
    yandex_on = Column(Boolean(), default=False)
    yandex_only_save = Column(Boolean(), default=False)
    yandex_token = Column(String(100))
    free_act = Column(Integer())
    create_at = Column(DateTime(timezone=False), default=func.now())
    bot_feedback = Column(String(10000))
    is_banned = Column(Boolean(), default=False)

    def __repr__(self):
        return f'<Telegram_user {self.id}>'


class TgGroup(Base):
    __tablename__ = 'tg_groups'
    id = Column(Integer(), primary_key=True)
    tg_chat_id = Column(BIGINT(), nullable=False, index=True, unique=True)
    lang = Column(String(4), default='en')
    yandex_on = Column(Boolean(), default=True)
    yandex_only_save = Column(Boolean(), default=False)
    yandex_token = Column(String(100))
    create_at = Column(DateTime(timezone=False), default=func.now())

    def __repr__(self):
        return f'<Group_id {self.id}>'


class TgActionApi(Base):
    __tablename__ = 'tg_actions'

    id = Column(Integer, primary_key=True)
    tg_user_id = Column(Integer, ForeignKey(TgUser.tg_user_id, ondelete='CASCADE'))
    tg_chat_id = Column(BIGINT(), index=True)
    tg_msg_id = Column(BIGINT(), index=True)
    api_url = Column(String(250), index=True)
    image_uuid = Column(String(50), index=True)
    is_success = Column(Boolean())
    add_info = Column(String(500))
    lang = Column(String(4))
    create_at = Column(DateTime(timezone=False), default=func.now())
    response = Column(String(20000))

    def __repr__(self):
        return f'<Telegram_user_action {self.telegram_user_id} {self.action}>'


class TgYandexDisk(Base):
    __tablename__ = 'tg_yandex_disk'
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(BIGINT(), index=True)
    tg_chat_id = Column(BIGINT(), index=True)
    tg_msg_id = Column(BIGINT(), index=True)
    token = Column(String(70))
    is_success = Column(Boolean(), default=True, index=True)
    file_path = Column(String(250))
    yandex_action = Column(ENUM(YandexAction))
    error = Column(String(1000))
    create_at = Column(DateTime(timezone=False), default=func.now())


    def __repr__(self):
        return f'<Yandexdisk_action {self.tg_message_id} {self.yandex_action} {self.file_path}>'


class TgChatHistory(Base):
    __tablename__ = 'tg_chat_history'
    id = Column(Integer, primary_key=True)
    type_update = Column(ENUM(TypeUpdate))
    tg_msg_id = Column(Integer(), index=True)
    tg_user_id = Column(Integer(), index=True)
    tg_chat_id = Column(BIGINT(), index=True)
    # user_msg = Column(String(10000))
    callback_data = Column(String(150))
    from_bot = Column(Boolean, default=True)
    is_image = Column(Boolean, default=False)
    file_id = Column(String(150), index=True)
    text = Column(String(10000))
    caption = Column(String(10000))
    content_type = Column(String(50))
    mime_type = Column(String(150))
    bot_message_edit = Column(Boolean, default=False)
    is_delete = Column(Boolean, default=False)
    create_at = Column(DateTime(timezone=False), default=func.now())


class CallbackQuery(Base):
    __tablename__ = 'rating_query'
    message_id = Column(Integer(), primary_key=True, index=True)
    image_uuid = Column(String(50))


async def async_create():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    asyncio.run(async_create())
