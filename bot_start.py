"""Bot start."""
import os
from aiogram import executor
from bot_init import  on_shutdown, on_startup
# from settings import (WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT)
from config import settings

from aiogram.utils.executor import start_webhook
# from dotenv import load_dotenv


if __name__ == '__main__':
    from handlers import dp
    from errors_handler import dp
    if settings.APP_METHOD == 'webhook':
        start_webhook(
            dispatcher=dp,
            webhook_path=settings.WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=settings.WEBAPP_HOST,
            port=settings.WEBAPP_PORT
        )
    else:
        executor.start_polling(dp, skip_updates=True)
