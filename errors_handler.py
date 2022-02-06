"""Errors handler."""
import logging
from asyncio.exceptions import TimeoutError

from aiogram.types.update import Update
from aiogram.utils.exceptions import (CantDemoteChatCreator, CantParseEntities,
                                      InvalidQueryID, MessageCantBeDeleted,
                                      MessageNotModified, MessageTextIsEmpty,
                                      MessageToDeleteNotFound, RetryAfter,
                                      TelegramAPIError, Unauthorized)

from aiohttp.client_exceptions import ClientError

from asyncpg.exceptions import (InterfaceError, InternalClientError,
                                PostgresError)

from bot_init import dp

from sqlalchemy.exc import SQLAlchemyError


@dp.errors_handler()
async def errors_handler(update: Update, exception):
    """Bot's error handler."""
    if isinstance(exception, CantDemoteChatCreator):
        logging.debug("Can't demote chat creator")
        return True

    if isinstance(exception, MessageNotModified):
        logging.debug('Message is not modified')
        return True
    if isinstance(exception, MessageCantBeDeleted):
        logging.debug('Message cant be deleted')
        return True

    if isinstance(exception, MessageToDeleteNotFound):
        logging.debug('Message to delete not found')
        return True

    if isinstance(exception, MessageTextIsEmpty):
        logging.debug('MessageTextIsEmpty')
        return True

    if isinstance(exception, Unauthorized):
        logging.info(f'Unauthorized: {exception}')
        return True

    if isinstance(exception, InvalidQueryID):
        logging.exception(f'InvalidQueryID: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, TelegramAPIError):
        logging.exception(f'TelegramAPIError: {exception} \nUpdate: {update}')
        return True
    if isinstance(exception, RetryAfter):
        logging.exception(f'RetryAfter: {exception} \nUpdate: {update}')
        return True
    if isinstance(exception, CantParseEntities):
        logging.exception(f'CantParseEntities: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, SQLAlchemyError):
        await send_message(update)
        logging.error(f'SQLAlchemyError: {exception} \nUpdate: {update}', exc_info=True)
        return True
    if isinstance(exception, ValueError):
        await send_message(update=update, text='<b>Service unavailable!</b>')
        logging.error(f'ValueError: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, TimeoutError):
        await send_message(update=update, text='<b>Service unavailable!</b>')
        logging.error(f'Asyncio TimeoutError: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, ClientError):
        logging.error(f'ClientError: {exception} \nUpdate: {update}', exc_info=True)
        await send_message(update=update, text='<b>Service client unavailable!</b>')
        return True
    if isinstance(exception, InterfaceError):
        await send_message(update)
        logging.critical(f'InterfaceError: {exception} \nUpdate: {update}', exc_info=True)
        return True
    if isinstance(exception, InternalClientError):
        await send_message(update)
        logging.critical(f'InternalClientError: {exception} \nUpdate: {update}', exc_info=True)
        return True
    if isinstance(exception, PostgresError):
        await send_message(update)
        logging.critical(f'PostgresError: {exception} \nUpdate: {update}', exc_info=True)
        return True
    logging.exception(f'Update: {update} \n{exception}')


async def send_message(update: Update, text=None):
    """Send message to user if server have problems."""
    if update:
        if not text:
            text = 'Sorry, server has problems!'
        await update.message.answer(text)
