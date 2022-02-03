"""Queries from DB."""
import logging
from typing import Any

from aiogram.types import Message

from db import TgUser, async_session

import settings

from sqlalchemy import update
from sqlalchemy.exc import InterfaceError, NoResultFound, SQLAlchemyError
from sqlalchemy.future import select


async def get_or_create_user_in_db(msg: Message):
    """Get or create user in DB."""
    tg_id = msg.from_user.id
    user = await get_user_from_db(tg_id)
    if not user:
        lang = getattr(msg.from_user, 'language_code', 'en')
        if lang not in settings.langs:
            lang = 'en'
        user = TgUser(tg_user_id=tg_id,
                      tg_user_name=getattr(msg.from_user, 'username', None),
                      first_name=getattr(msg.from_user, 'first_name', None),
                      last_name=getattr(msg.from_user, 'username', None),
                      lang=lang)
        add_success = await add_object_to_db(user)
        if not add_success:
            user = None
    return user


async def add_object_to_db(obj):
    """Add object to DB."""
    try:
        async with async_session() as session:
            session.add(obj)
            await session.commit()
    except (SQLAlchemyError, InterfaceError) as e:
        await session.rollback()
        logging.exception(f'SQLAlchemyError: {e}')
        return False
    return True


async def get_user_from_db(tg_user_id):
    """Get user from DB."""
    query = select(TgUser).where(TgUser.tg_user_id == tg_user_id)
    async with async_session() as session:
        result = await session.execute(query)
    try:
        (user, ) = result.one()
    except NoResultFound:
        user = None
    return user


async def update_user(tg_user_id, **kwargs):
    """Update users atributes."""
    query = (update(TgUser).where(TgUser.tg_user_id == tg_user_id)
             .values(**kwargs))
    try:         
        async with async_session() as session:
            await session.execute(query)
            await session.commit()
    except (SQLAlchemyError, InterfaceError) as e:
        await session.rollback()
        logging.exception(f'SQLAlchemyError: {e}')
        return False
    return True
