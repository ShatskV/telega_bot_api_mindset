"""Errors handler."""
import logging
from asyncio.exceptions import TimeoutError

from aiogram.utils.exceptions import (CantDemoteChatCreator, CantParseEntities,
                                      InvalidQueryID, MessageCantBeDeleted,
                                      MessageNotModified, MessageTextIsEmpty,
                                      MessageToDeleteNotFound, RetryAfter,
                                      TelegramAPIError, Unauthorized)

from aiohttp import ClientError

from bot_init import dp

from sqlalchemy.exc import SQLAlchemyError


@dp.errors_handler()
async def errors_handler(update, exception):

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

    if isinstance(exception, TimeoutError):
        logging.exception(f'Asyncio TimeoutError: {exception} \nUpdate: {update}')
        return True
    if isinstance(exception, SQLAlchemyError):
        logging.exception(f'SQLAlchemyError: {exception} \nUpdate: {update}')
        return True
    if isinstance(exception, ClientError):
        logging.exception(f'ClientError: {exception} \nUpdate: {update}')
        return True
    if isinstance(exception, ValueError):
        logging.exception(f'ValueError: {exception} \nUpdate: {update}')
        return True

    logging.exception(f'Update: {update} \n{exception}')
