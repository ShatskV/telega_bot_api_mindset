import pprint
import json
import logging
import os
import requests
from dotenv import load_dotenv
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext, storage
import warnings
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, document, message
from sqlalchemy.sql.expression import text
from utils import get_desc_and_tags, set_result_rating, silentremove, form_file_path_url
from aiogram import types
from aiogram.types import ContentType

from aiogram.contrib.fsm_storage.memory import MemoryStorage

with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
storage = MemoryStorage()
load_dotenv() 
API_TOKEN = os.environ.get('API_TOKEN')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


class ImageDlg(StatesGroup):
    action = State()
    rating = State()
    ru = State()
    # end = State() 


inline_btn_desc_ru = InlineKeyboardButton('Описание и теги на русском', callback_data='desc_ru')
inline_btn_desc_en = InlineKeyboardButton('Description and tags on english', callback_data='desc_en')
inline_kb_desc = InlineKeyboardMarkup().add(inline_btn_desc_ru)
inline_kb_desc.add(inline_btn_desc_en)

inline_btn_rat_1 = InlineKeyboardButton('1', callback_data='rat_1')
inline_btn_rat_2 = InlineKeyboardButton('2', callback_data='rat_2')
inline_btn_rat_3 = InlineKeyboardButton('3', callback_data='rat_3')
inline_btn_rat_4 = InlineKeyboardButton('4', callback_data='rat_4')
inline_btn_rat_5 = InlineKeyboardButton('5', callback_data='rat_5')
inline_kb_rat = InlineKeyboardMarkup().row(inline_btn_rat_1, inline_btn_rat_2, inline_btn_rat_3, 
                                                inline_btn_rat_4, inline_btn_rat_5)


# @dp.message_handler(lambda message: message.text and message.text.lower().startswith('http'), content_types=['text'])
# async def get_desc_and_tags_url(message: types.Message, state: FSMContext):
    
#     await message.reply("url получен")
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('rat'), state=ImageDlg.rating)
async def process_callback_rating(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    rating = int(callback_query.data[-1])
    async with state.proxy() as data:
        answer = set_result_rating(uuid=data['uuid'], rating=rating)
        data['message_id'] = callback_query.message.message_id
    await state.finish()
    await bot.edit_message_text(chat_id=callback_query.from_user.id, 
                message_id=callback_query.message.message_id, text='Спасибо за оценку!')
    if rating in [4,5]:            
        await bot.send_sticker(callback_query.from_user.id, 
                sticker='CAACAgIAAxkBAAEDh6BhwO-eB4xfFmR-mQ1HMwQ428C0jgACQQADKA9qFPDp0yN1HEZhIwQ')
    if rating in [1,2]:
        await bot.send_sticker(callback_query.from_user.id, 
                sticker='CAACAgIAAxkBAAEDiP5hwgLDNwcNTzgrDu8ZZ2YNvq_fUAACiAEAAjDUnRGjlneuNUhvFCME')
    if rating == 3: 
        await bot.send_sticker(callback_query.from_user.id, 
                sticker='CAACAgIAAxkBAAEDiQdhwgPcAkOhbWaFMp5rl178jlICmQACmgADO2AkFBhQ2N6IkxSUIwQ')


# @dp.callback_query_handler(state=ImageDlg.rating)
@dp.message_handler(lambda message: 'image/' in message.document.mime_type , content_types='document')
@dp.message_handler(lambda message: message.text and message.text.lower().startswith('http'), state='*')
@dp.message_handler(content_types=['photo'], state='*')
async def get_desc_and_tags_file(message: types.Message, state: FSMContext):
    del_path = os.path.join('downloads', str(message.from_user.id))
    silentremove(del_path)
    async with state.proxy() as data:
        if data.get('message_id'):
            await bot.edit_message_text(chat_id=message.from_user.id, 
                message_id=data['message_id']+1,
                text='Действие не выбрано!', reply_markup=None)
    await state.reset_state()

    filename, is_url = await form_file_path_url(message)
    async with state.proxy() as data:
        data['path_url'] = filename
        data['is_url'] = is_url
        data['message_id'] = message.message_id
    await ImageDlg.action.set()
    await message.reply("Что выхотите сделать с фото?", reply_markup=inline_kb_desc)
    
    
# @dp.message_handler(state=ImageDlg.action)
# async def process_action(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         await message.reply(f"path = {data['path']}")
#     await ImageDlg.next()
#     await message.reply(f'Ваша оценка?')


# @dp.message_handler(state=ImageDlg.end)
# async def process_rating(message: types.Message, state: FSMContext):
#     await state.finish()
#     await message.reply(f'диалог завершен!')




@dp.callback_query_handler(lambda c: c.data and c.data.startswith('rat'), state=ImageDlg.ru)
async def process_callback_ru(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.send_message(callback_query.from_user.id, 'я в ру')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('desc'), state=ImageDlg.action)
async def process_callback_desc(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    lang = callback_query.data[-2:]
    async with state.proxy() as data:
        path = data['path_url']
        answer, uuid = get_desc_and_tags(path_url=path, lang=lang, url_method=data.get('is_url'))
        data['uuid'] = uuid
        data['message_id'] = callback_query.message.message_id

   
    # await bot.delete_message(chat_id=callback_query.from_user.id, 
                # message_id=callback_query.message.message_id)
    if lang == 'en':
        await ImageDlg.next()
    else: 
        await state.set_state(ImageDlg.ru)
    # await bot.send_message(callback_query.from_user.id, answer)
    await bot.edit_message_text(chat_id=callback_query.from_user.id, 
                message_id=callback_query.message.message_id, text=answer)
    await bot.send_message(callback_query.from_user.id, f'Оцените результат, пожалуйста! {callback_query}', reply_markup=inline_kb_rat)





# @dp.callback_query_handler(lambda c: c.data=='button2', state=ImageDlg.action)
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


@dp.message_handler(lambda message: 'image/' in message.document.mime_type , content_types=ContentType.DOCUMENT)
async def recieve_file(message: types.Message, state: FSMContext):
    # photo = message.photo.pop()

    # print(f'PHOTO! {photo}')
    print('PHOTO')
    print(message)


@dp.message_handler()
async def echo(message: types.Message):
    print(message)
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)