"""Queries from DB."""
from typing import Union
import logging

from aiogram.types import Message
from aiogram.types import CallbackQuery as Callback

from asyncpg.exceptions import (InterfaceError, InternalClientError,
                                PostgresError)

from db import TgChatHistory, TgGroup, TgUser, CallbackQuery, TgYandexDisk, async_session
from history_utils import create_api_history
from config import settings

from sqlalchemy import update
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.future import select


async def get_or_create_user_in_db(msg: Message):
    """Get or create user in DB."""
    tg_user_id = msg.from_user.id
    user = await get_user_from_db(tg_user_id)
    if not user:
        lang = getattr(msg.from_user, 'language_code', 'en')
        if lang not in settings.langs:
            lang = 'en'
        user = TgUser(tg_user_id=tg_user_id,
                      tg_user_name=getattr(msg.from_user, 'username', None),
                      first_name=getattr(msg.from_user, 'first_name', None),
                      last_name=getattr(msg.from_user, 'last_name', None),
                      lang=lang)
        await add_object_to_db(user)
        # if not add_success:
        #     user = None
    return user


async def get_or_create_group_in_db(msg: Message):
    """Get or create user in DB."""
    group_id = msg.chat.id
    group = await get_group_from_db(group_id)
    if not group:
        lang = getattr(msg.from_user, 'language_code', 'en')
        if lang not in settings.langs:
            lang = 'en'
        group = TgGroup(tg_chat_id=group_id,
                        lang=lang)
        # print(f'_______{group.tg_chat_id, group.yandex_token}_______')
        await add_object_to_db(group)
        # if not add_success:
        #     group = None
    return group


async def update_user(msg: Message, **kwargs):
    """Update user atributes."""
    tg_user_id = msg.from_user.id
    await get_or_create_user_in_db(msg)
    # query = (update(TgUser).where(TgUser.tg_user_id == tg_user_id)
            #  .values(**kwargs))
    await update_obj_in_db(cls=TgUser,
                           cls_atr='tg_user_id',
                           atr_val=tg_user_id,
                           **kwargs)


async def update_group(msg: Message, **kwargs):
    """Update user atributes."""
    tg_chat_id = msg.chat.id
    await get_or_create_group_in_db(msg)
    # query = (update(TgUser).where(TgUser.tg_user_id == tg_user_id)
            #  .values(**kwargs))
    await update_obj_in_db(cls=TgGroup,
                           cls_atr='tg_chat_id',
                           atr_val=tg_chat_id,
                           **kwargs)

async def get_message(message_id):
    """Get message from DB."""
    result = await get_obj_from_db(cls=TgChatHistory,
                                   cls_atr='tg_msg_id',
                                   atr_val=message_id)
    try:
        (message, ) = result.first()
    except NoResultFound:
        message = None
    return message


async def update_message(message_id, **kwargs):
    message = await get_message(message_id=message_id)
    if message:
        await update_obj_in_db(cls=TgChatHistory,
                               cls_atr='id',
                               atr_val=message.id,
                               **kwargs)


async def get_user_from_db(tg_user_id):
    """Get user from DB."""
    # query = select(TgUser).where(TgUser.tg_user_id == tg_user_id)
    result = await get_obj_from_db(cls=TgUser,
                                   cls_atr='tg_user_id',
                                   atr_val=tg_user_id)
    try:
        (user, ) = result.one()
    except NoResultFound:
        user = None
    return user


async def get_group_from_db(tg_chat_id):
    """Get user from DB."""
    # query = select(TgUser).where(TgUser.tg_user_id == tg_user_id)
    result = await get_obj_from_db(cls=TgGroup,
                                   cls_atr='tg_chat_id',
                                   atr_val=tg_chat_id)
    try:
        (group, ) = result.one()
    except NoResultFound:
        group = None
    return group


async def add_rating_query(msg_id, uuid):
    msg = CallbackQuery(message_id=msg_id,
                        image_uuid=uuid)
    await add_object_to_db(msg)


async def add_api_history(msg: Union[Message, Callback], url, payload, result):
    cls_api = create_api_history(msg=msg, url=url, payload=payload, result=result)
    await add_object_to_db(cls_api)


async def add_yandex_query(ya_log, message: Union[Message, Callback]):
    if isinstance(message, Callback):
        message = message.message
    is_success = False if ya_log.get('error', False) else True
    ya_his = TgYandexDisk(tg_user_id=message.from_user.id,
                          tg_chat_id=message.chat.id,
                          tg_msg_id=message.message_id,
                          token=ya_log.get('token', None),
                          is_success=is_success,
                          file_path=ya_log.get('file_path'),
                          yandex_action=ya_log.get('action'),
                          error=ya_log.get('error')
                          )
    await add_object_to_db(ya_his)


async def get_uuid_from_db_query(msg_id):
    """Get user from DB."""
    result = await get_obj_from_db(cls=CallbackQuery,
                                   cls_atr='message_id',
                                   atr_val=msg_id)
    try:
        (msg, ) = result.one()
    except NoResultFound:
        uuid = None
    else:
        uuid = msg.image_uuid
    return uuid


async def get_obj_from_db(cls, cls_atr, atr_val, **kwargs):
    """Get object from DB."""
    query = select(cls).where(getattr(cls, cls_atr) == atr_val)
    try:
        async with async_session() as session:
            result = await session.execute(query)
            await session.commit()
    except SQLAlchemyError as e:
        logging.error('SQLAlchemy error!')
        await session.rollback()
        raise e
    except (InterfaceError, InternalClientError,
            PostgresError) as e:
        logging.critical('Connection DB problem!')
        raise e
    finally:
        await session.close()
    return result


async def add_messages_to_db(list_msgs):
    """Add messages to DB."""
    try:
        async with async_session() as session:
            # for msg in list_msgs:
            session.add_all(list_msgs)
                # session.add(msg)
            await session.commit()
    except SQLAlchemyError as e:
        logging.error('SQLAlchemy error!')
        await session.rollback()
        raise e
    except (InterfaceError, InternalClientError,
            PostgresError) as e:
        logging.critical('Connection DB problem!')
        raise e
    finally:
        await session.close()


async def add_object_to_db(obj):
    """Add object to DB."""
    try:
        async with async_session() as session:
            session.add(obj)
            await session.commit()
    except SQLAlchemyError as e:
        logging.error('SQLAlchemy error!')
        await session.rollback()
        raise e
    except (InterfaceError, InternalClientError,
            PostgresError) as e:
        logging.critical('Connection DB problem!')
        raise e
    finally:
        await session.close()


async def update_obj_in_db(cls, cls_atr, atr_val, **kwargs):
    """Update object in DB."""
    query = (update(cls).where(getattr(cls, cls_atr) == atr_val)
             .values(**kwargs))
    try:
        async with async_session() as session:
            await session.execute(query)
            await session.commit()
    except SQLAlchemyError as e:
        logging.error('SQLAlchemy error!')
        await session.rollback()
        raise e
    except (InterfaceError, InternalClientError,
            PostgresError) as e:
        logging.critical('Connection DB problem!')
        raise e

    finally:
        await session.close()
