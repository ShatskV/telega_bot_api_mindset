
import logging
import os
import requests
# from requests import post
from dotenv import load_dotenv
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext, storage
import warnings
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils import get_desc_and_tags

from aiogram.contrib.fsm_storage.memory import MemoryStorage

with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
storage = MemoryStorage()
load_dotenv() 
API_TOKEN = os.environ.get('API_TOKEN')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    action = State()
    rating = State()


inline_btn_desc_ru = InlineKeyboardButton('Описание и теги на русском', callback_data='desc_ru')
inline_btn_desc_en = InlineKeyboardButton('Description and tags on english', callback_data='desc_en')
inline_kb_desc = InlineKeyboardMarkup().add(inline_btn_desc_ru)
inline_kb_desc.add(inline_btn_desc_en)



@dp.message_handler(content_types=['photo'])
async def get_desc_and_bots(message: types.Message, state: FSMContext):
    os.makedirs('downloads', exist_ok=True)
    file_name = os.path.join('downloads', f'{message.photo[-1].file_id}.jpg')
    await message.photo[-1].download(file_name)
    async with state.proxy() as data:
        data['path'] = file_name
    await Form.action.set()
    await message.reply("Что выхотите сделать с фото?", reply_markup=inline_kb_desc)
    
    
# @dp.message_handler(state=Form.action)
# async def process_action(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         await message.reply(f"path = {data['path']}")
#     await Form.next()
#     await message.reply(f'Ваша оценка?')


@dp.message_handler(state=Form.rating)
async def process_rating(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply(f'диалог завершен!')
    

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('desc'), state=Form.action)
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=callback_query.from_user.id, 
                message_id=callback_query.message.message_id)
    lang = callback_query.data[-2:]
    async with state.proxy() as data:
        path = data['path']
    answer = get_desc_and_tags(path=path, lang=lang)
    if 'error' in answer: 
        answer = "Сервер не доступен"
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, answer)


# @dp.callback_query_handler(lambda c: c.data=='button2', state=Form.action)
# async def process_callback_button2(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await bot.send_message(callback_query.from_user.id, 'Нажата вторая кнопка!')


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    payload = {'email': 'vova@example.com',
               'password': 'test1'}
    api_route = '/api/auth/login'
    url = 'http://app-staging.picpack.io:80'
    url = url + api_route
    response = requests.post(url, json=payload, timeout=(3,7))
    result = response.json()
    
    await message.reply(f"Hi!\nI'm EchoBot!\nresult = {result}")


@dp.message_handler(commands=['user'])
async def send_welcome(message: types.Message):
    
    path = 'gruz.jpg'
    api_route = '/api/demo/description/file'
    url = 'http://app-staging.picpack.io:80'
    url = url + api_route
    files = {'image_file': open(path, 'rb')}
    data = {'lang': 'en'}
    response = requests.post(url, files=files, data=data, timeout=(3,7))
    result = response.json()
    answer = f"description: {result.get('description')}\ntags:\n"
    if result.get('tags'):
        for tag in result['tags']:
            if tag['confidence'] > 0.2:
                answer += f"{tag['tag']}: {tag['confidence']}\n" 

    await message.reply(f"result = {answer}")


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)