
import logging
import os
import requests
# from requests import post
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, executor, types
 

load_dotenv() 
API_TOKEN = os.environ.get('API_TOKEN')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    payload = {'email': 'vova@example.com',
               'password': 'test1'}
    api_route = '/api/auth/login'
    url = 'http://172.20.0.6:5000'
    url = url + api_route
    response = requests.post(url, json=payload, timeout=(3,7))
    result = response.json()
    
    await message.reply(f"Hi!\nI'm EchoBot!\nresult = {result}")


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)