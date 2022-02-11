"""Queries from DB."""
import logging

from aiogram.types import Message

from asyncpg.exceptions import (InterfaceError, InternalClientError,
                                PostgresError)

from db import TgUser, async_session

import settings

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
                      last_name=getattr(msg.from_user, 'username', None),
                      lang=lang)
        add_success = await add_object_to_db(user)
        if not add_success:
            user = None
    return user


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


