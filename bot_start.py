"""Bot start."""
import os
from aiogram import executor
from bot_init import (WEBHOOK_PATH, on_shutdown, on_startup,
                      WEBAPP_HOST, WEBAPP_PORT)

from aiogram.utils.executor import start_webhook
from dotenv import load_dotenv


load_dotenv()
APP_METHOD = os.environ.get('APP_METHOD')
if __name__ == '__main__':
    from handlers import dp
    from errors_handler import dp
    if APP_METHOD == 'webhook':
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
    else:
        executor.start_polling(dp, skip_updates=True)
