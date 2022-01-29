import logging
import os
import requests
from dotenv import load_dotenv
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext, storage
import warnings
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, document, message
from utils import (async_get_desc, async_set_rating, silentremove, form_file_path_url)
from aiogram import types
from aiogram.types import ContentType
from aiogram.utils.exceptions import MessageTextIsEmpty
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from db import TagFormat
import settings
from queiries import get_or_create_user_in_db, update_user
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
storage = MemoryStorage()
load_dotenv() 
API_TOKEN = os.environ.get('API_TOKEN')
logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)


class ImageDlg(StatesGroup):
    rating = State()


class ChangeTags(StatesGroup):
    choose = State()


class ChangeLang(StatesGroup):
    choose = State()


class ChangeRateSet(StatesGroup):
    choose = State()

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

inline_btn_tag1 = InlineKeyboardButton('#tag1 #tag2 #tag3', callback_data='tags_instagram')
inline_btn_tag2 = InlineKeyboardButton('tag1, tag2, tag3', callback_data='tags_list_tags')
inline_kb_tags = InlineKeyboardMarkup().add(inline_btn_tag1)
inline_kb_tags.add(inline_btn_tag2)

inline_btn_lang_ru = InlineKeyboardButton('Русский', callback_data='lang_ru')
inline_btn_lang_en = InlineKeyboardButton('English', callback_data='lang_en')
inline_kb_langs = InlineKeyboardMarkup().add(inline_btn_lang_ru)
inline_kb_langs.add(inline_btn_lang_en)
inline_btn_rate_1 = InlineKeyboardButton('On', callback_data='rating_1')
inline_btn_rate_0 = InlineKeyboardButton('Off', callback_data='rating_0')
inline_kb_rating = InlineKeyboardMarkup().row(inline_btn_rate_0, inline_btn_rate_1)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('rating'), state=ChangeRateSet.choose)
async def process_callback_rating(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    rating = callback_query.data[-1:]
    await get_or_create_user_in_db(callback_query)
    rating = bool(int(rating))
    await update_user(callback_query.from_user.id, rating=rating)
    await state.finish()
    if rating:
        rating = 'on'
    else: 
        rating = 'off'
    await bot.edit_message_text(chat_id=callback_query.from_user.id, 
                message_id=callback_query.message.message_id, text=f'Rating was turned {rating}')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('lang'), state=ChangeLang.choose)
async def process_callback_rating(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    new_lang = callback_query.data[-2:]
    await get_or_create_user_in_db(callback_query)
    await update_user(callback_query.from_user.id, lang=new_lang)
    await state.finish()
    await bot.edit_message_text(chat_id=callback_query.from_user.id, 
                message_id=callback_query.message.message_id, text=f'Language was changed to English!')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('tags'), state=ChangeTags.choose)
async def process_callback_rating(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    tags_fmt = callback_query.data[5:]
    await get_or_create_user_in_db(callback_query)
    tags_format = getattr(TagFormat, tags_fmt)
    await update_user(callback_query.from_user.id, tags_format=tags_format)
    await state.finish()
    # tag_value = tags_format.value
    await state.finish()
    await bot.edit_message_text(chat_id=callback_query.from_user.id, 
                message_id=callback_query.message.message_id, text=f'Tags format change to {tags_format.value}')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('rat'), state=ImageDlg.rating)
async def process_callback_rating(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    rating = int(callback_query.data[-1])
    async with state.proxy() as data:
        await async_set_rating(uuid=data['uuid'], rating=rating)
        lang = data['lang']
    await state.finish()
    await bot.edit_message_text(chat_id=callback_query.from_user.id, 
                message_id=callback_query.message.message_id, text='Thank you for rating!')


@dp.message_handler(lambda message: 'image/' in message.document.mime_type , content_types='document', state='*')
@dp.message_handler(lambda message: message.text and message.text.lower().startswith('http'), state='*')
@dp.message_handler(content_types=['photo'], state='*')
async def get_desc_and_tags_image(message: types.Message, state: FSMContext):
    await state.reset_state()

    user = await get_or_create_user_in_db(message)
    
    filename, is_url = await form_file_path_url(message)
    async with state.proxy() as data:
        data['lang'] = user.lang
    answer, uuid = await async_get_desc(path_url=filename, 
                                        lang=user.lang, 
                                        tags_format=user.tags_format.value,
                                        url_method=is_url)
    await state.update_data(uuid = uuid)
    del_path = os.path.join('downloads', str(message.from_user.id))
    silentremove(del_path)
    for item in answer:
        await message.answer(item)
    if user.rating:
        await ImageDlg.rating.set()
        await state.update_data(inline=True)
        await message.reply(f'Please, rate the result!', reply_markup=inline_kb_rat)


@dp.message_handler(commands='rating', state='*')
async def rating_off(message: types.Message, state: FSMContext):
    rating = message.get_args()
    if not rating:
        await ChangeRateSet.choose.set()
        await message.answer('Choose rating setting:', reply_markup=inline_kb_rating)
        return
    rating = rating.lower()
    if rating in ['1', '0', 'on', 'off']:
        if rating in ['1', 'on']:
            rating = True
        else:
            rating = False
        await get_or_create_user_in_db(message)
        await update_user(message.from_user.id, rating=rating)
        if rating: 
            rating = 'on'
        else:
            rating = 'off'
        await message.answer(f'Rating was turned {rating}')
    else: 
        await message.answer('Wrong format! Should be /rating + 1/0/on/off')


@dp.message_handler(commands='lang', state='*')
async def change_lang(message: types.Message, state: FSMContext):
    new_lang = message.get_args()
    if not new_lang:
        await ChangeLang.choose.set()
        await message.answer('Choose your language', reply_markup=inline_kb_langs)
        return
    if new_lang in settings.langs:
        await get_or_create_user_in_db(message)
        await update_user(message.from_user.id, lang=new_lang)
        await message.answer(f'Language was change to English!')
    else: 
        await message.answer('Language not supported or wrong format!')


@dp.message_handler(commands='tags', state='*')
async def tags_format(message: types.Message, state: FSMContext):
    tags_fmt = message.get_args()
    if not tags_fmt:
        await ChangeTags.choose.set()
        await message.answer('Choose tags format:', reply_markup=inline_kb_tags)
        return 
    tags_fmt = tags_fmt.lower()
    if tags_fmt in TagFormat:
        await get_or_create_user_in_db(message)
        if tags_fmt == 'list':
            tags_fmt += '_tags'
        tags_fmt = getattr(TagFormat, tags_fmt)
        await update_user(message.from_user.id, tags_format=tags_fmt)
        await message.answer(f'Tags format change to {tags_fmt.value}')
    else:
        await message.answer('Wrong tags format!')


@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    await message.reply(f"Hi!\nI'm EchoBot!\nresult")


async def check_edit_keyboard_message(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        async with state.proxy() as data:
            if data.get('inline'):
                await bot.edit_message_text(chat_id=msg.from_user.id, 
                    message_id=msg.message_id-1,
                    text='No action selected!', reply_markup=None)
    state.finish()


@dp.message_handler(content_types=['text'], state='*')
async def echo(message: types.Message, state):
    await message.answer("Don't understand you!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)