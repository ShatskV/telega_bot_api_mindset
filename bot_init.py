import logging
import os
from dotenv import load_dotenv

from aiogram.dispatcher import storage
import warnings
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from lang_middleware import setup_middleware

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)

storage = MemoryStorage()
load_dotenv() 
API_TOKEN = os.environ.get('API_TOKEN')
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)
# logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)

i18n = setup_middleware(dp)
_ = i18n.gettext