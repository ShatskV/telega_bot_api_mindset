"""Init bot and extensions."""
import logging
import os
import warnings

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from dotenv import load_dotenv

from lang_middleware import setup_middleware

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=DeprecationWarning)
from config import settings

storage = MemoryStorage()
load_dotenv()
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=settings.LOG_LEVEL)

bot = Bot(token=settings.API_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)

i18n = setup_middleware(dp)
_ = i18n.gettext

async def on_startup(dp):
    await bot.set_webhook(settings.WEBHOOK_URL)

async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()
