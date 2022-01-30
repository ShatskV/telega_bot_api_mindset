from email import message
import logging
from db import async_session, TgUser
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from aiogram.types import Message
from sqlalchemy.exc import SQLAlchemyError, InterfaceError
import settings
async def get_or_create_user_in_db(msg: Message):
    tg_id = msg.from_user.id
    user = await get_user_from_db(tg_id)
    if not user:
        lang = getattr(msg.from_user, 'language_code', 'en')
        if not lang in settings.langs:
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
    try:
        async with async_session() as session:
            session.add(obj)
            await session.commit()
    except (SQLAlchemyError, InterfaceError)  as e:
        await session.rollback()
        logging.exception(f'SQLAlchemyError: {e}')
        return False
    return True
        

async def get_user_from_db(tg_user_id):
    query = select(TgUser).where(TgUser.tg_user_id == tg_user_id)
    async with async_session() as session:
        result = await session.execute(query)
    try:
        (user, ) = result.one()
    except NoResultFound:
        user = None
    return user


async def update_user(tg_user_id, **kwargs):
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
