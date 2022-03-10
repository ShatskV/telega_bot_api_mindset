"""Bot's handlers."""
from distutils.command import check
import logging
import os

from aiogram import filters, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot_init import _, bot, dp
from config import settings
from db import TagFormat
from queiries import (add_rating_query, get_or_create_group_in_db,
                      get_or_create_user_in_db, get_uuid_from_db_query,
                      update_group, update_user)
from utils import (async_get_desc, async_set_rating, check_answer_yandex, check_args_bool,
                   form_file_path_url, make_desc_tags_answer,
                   make_tag_folder_for_yandex, silentremove)
from yandex_disk import yandex_check, yandex_upload


class ImageDlg(StatesGroup):
    """States for image dialog."""

    rating = State()


class ChangeTags(StatesGroup):
    """States for change format dialog."""

    choose = State()


class ChangeLang(StatesGroup):
    """States for change lang dialog."""

    choose = State()


class ChangeRateSet(StatesGroup):
    """States for change rating setting dialog."""

    choose = State()


class Feedback(StatesGroup):
    """States for feedback dialog."""

    leave = State()


def get_tag_name(key):
    tags_format_dict = {'list': _('list'),
                        'instagram': _('instagram')}
    return tags_format_dict.get(key)


# inline_btn_desc_ru = InlineKeyboardButton('Описание и теги на русском', callback_data='desc_ru')
# inline_btn_desc_en = InlineKeyboardButton('Description and tags on english', callback_data='desc_en')
# inline_kb_desc = InlineKeyboardMarkup().add(inline_btn_desc_ru)
# inline_kb_desc.add(inline_btn_desc_en)

inline_btn_rat_1 = InlineKeyboardButton('1', callback_data='rat_1')
inline_btn_rat_2 = InlineKeyboardButton('2', callback_data='rat_2')
inline_btn_rat_3 = InlineKeyboardButton('3', callback_data='rat_3')
inline_btn_rat_4 = InlineKeyboardButton('4', callback_data='rat_4')
inline_btn_rat_5 = InlineKeyboardButton('5', callback_data='rat_5')
inline_kb_rat = InlineKeyboardMarkup().row(inline_btn_rat_1, inline_btn_rat_2, inline_btn_rat_3,
                                           inline_btn_rat_4, inline_btn_rat_5)


inline_btn_lang_ru = InlineKeyboardButton('Русский', callback_data='lang_ru')
inline_btn_lang_en = InlineKeyboardButton('English', callback_data='lang_en')
inline_kb_langs = InlineKeyboardMarkup().add(inline_btn_lang_ru)
inline_kb_langs.add(inline_btn_lang_en)


def get_tag_kb():
    inline_btn_tag1 = InlineKeyboardButton(_('#tag1 #tag2 #tag3'), callback_data='tags_instagram')
    inline_btn_tag2 = InlineKeyboardButton(_('tag1, tag2, tag3'), callback_data='tags_list_tags')
    inline_kb_tags = InlineKeyboardMarkup().add(inline_btn_tag1)
    inline_kb_tags.add(inline_btn_tag2)
    return inline_kb_tags


def get_rate_kb():
    inline_btn_rate_1 = InlineKeyboardButton(_('On'), callback_data='rating_1')
    inline_btn_rate_0 = InlineKeyboardButton(_('Off'), callback_data='rating_0')
    inline_kb_rating = InlineKeyboardMarkup().row(inline_btn_rate_0, inline_btn_rate_1)
    return inline_kb_rating


group_chat = ChatTypeFilter(chat_type=['group', 'supergroup'])
private_chat = ChatTypeFilter(chat_type=types.ChatType.PRIVATE)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('rating'), state='*')
async def process_callback_rating(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    rating = callback_query.data[-1:]
    rating = int(rating)
    await get_or_create_user_in_db(callback_query)
    await update_user(callback_query, rating=rating)
    if rating:
        rating = _('on')
    else:
        rating = _('off')
    await state.finish()
    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text=_('Rating was turned {state}').format(state=rating))


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('lang'), state='*')
async def process_callback_rating(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    new_lang = callback_query.data[-2:]
    await update_user(callback_query, lang=new_lang)
    await state.reset_state(with_data=False)
    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text=_('Language was changed to English!', locale=new_lang))


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('tags'), state='*')
async def process_callback_rating(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    tags_fmt = callback_query.data[5:]
    tags_format = getattr(TagFormat, tags_fmt)
    await update_user(callback_query, tags_format=tags_format)
    await state.reset_state(with_data=False)
    tag_format = get_tag_name(tags_format.value)
    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text=_('Tags format was changed to {fmt}').format(fmt=tag_format))


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('rat_'), state='*')
async def process_callback_rating(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    rating = int(callback_query.data[-1])
    call_msg_id = callback_query.message.message_id
    async with state.proxy() as data:
        uuid = data.get('uuid')
        msg_id = data.get('msg_id')
    if msg_id == call_msg_id:
        await state.reset_data()
        if not uuid:
            uuid = await get_uuid_from_db_query(msg_id=msg_id)
    else:
        uuid = await get_uuid_from_db_query(msg_id=call_msg_id)
    if uuid:
        await async_set_rating(uuid=uuid, rating=rating)
    else:
        logging.error('No uuid for rating!')

    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=call_msg_id,
                                text=_('Thank you for rating!'))


@dp.message_handler(private_chat, lambda message: 'image/' in message.document.mime_type, content_types='document', state='*')
@dp.message_handler(private_chat, lambda message: message.text and message.text.lower().startswith('http'), state='*')
@dp.message_handler(private_chat, content_types=['photo'], state='*')
async def get_desc_and_tags_image(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    user = await get_or_create_user_in_db(message)
    filename, is_url = await form_file_path_url(message)

    result = await async_get_desc(path_url=filename,
                                  lang=user.lang,
                                  url_method=is_url)
    answer, uuid = make_desc_tags_answer(result=result, tags_format=user.tags_format.value)
    ya_token = user.yandex_token
    yandex_answer = None
    if user.yandex_on and ya_token:
        tag_folder, uuid = make_tag_folder_for_yandex(result)
        upload_success = await yandex_upload(tag=tag_folder,
                                             uuid=uuid,
                                             filename=filename,
                                             token=user.yandex_token)
        yandex_answer = check_answer_yandex(upload_success)
    # async with state.proxy() as data:
    #     data['uuid'] = uuid
    await state.update_data(uuid=uuid)

    del_path = os.path.join('downloads', str(message.from_user.id))
    silentremove(del_path)
    for item in answer:
        last_msg = await message.answer(item)
    if not ya_token and user.yandex_on:
        await message.reply(_('No token for Yandex.disk! Please, recieve token:\n{url}\nAnd add with '
                              .format(url=settings.YADISK_AUTH_URL) + 'command /yadisk_token RECIEVED_TOKEN'))
        return
    if yandex_answer:
        await message.reply(yandex_answer)
    if user.rating:
        msg_id = last_msg.message_id + 1
        await state.update_data(msg_id=msg_id)
        await add_rating_query(msg_id=msg_id, uuid=uuid)
        await message.reply(_('Please, rate the result!'), reply_markup=inline_kb_rat)


@dp.message_handler(private_chat, commands='rating', state='*')
async def rating_off(message: types.Message, state: FSMContext):
    rating = message.get_args()
    await state.reset_state(with_data=False)

    if not rating:
        # await ChangeRateSet.choose.set()
        await message.answer(_('Choose rating setting:'), reply_markup=get_rate_kb())
        return
    rating = check_args_bool(rating)
    await update_user(message, rating=rating)
    if rating is None:
        await message.answer(_('Wrong format! Should be /rating 1/0/on/off'))
    if rating:
        rating = _('on')
    else:
        rating = _('off')
        await message.answer(_('Rating was turned {}').format(rating))


@dp.message_handler(commands='lang', state='*')
async def change_lang(message: types.Message, state: FSMContext):
    new_lang = message.get_args()
    await state.reset_state(with_data=False)

    if not new_lang:
        # await ChangeLang.choose.set()
        if message.chat.id > 0:
            await message.reply(_('Choose your language:'), reply_markup=inline_kb_langs)
        else:
            await message.reply(_('No arguments! Should be /lang {lang}'.format(lang='/'.join(settings.langs))))
        return
    if new_lang in settings.langs:
        if message.chat.id < 0:
            await update_user(message, lang=new_lang)
        else:
            await update_group(message, lang=new_lang)
        await message.answer(_('Language was change to English!', locale=new_lang))
    else:
        await message.answer(_('Language not supported or wrong format!'))


@dp.message_handler(private_chat, commands='tags', state='*')
async def tags_format(message: types.Message, state: FSMContext):
    tags_fmt = message.get_args()
    await state.reset_state(with_data=False)

    if not tags_fmt:
        # await ChangeTags.choose.set()
        await message.answer(_('Choose tags format:'), reply_markup=get_tag_kb())
        return
    tags_fmt = tags_fmt.lower()
    if tags_fmt in TagFormat:
        if tags_fmt == 'list':
            tags_fmt += '_tags'
        tags_fmt = getattr(TagFormat, tags_fmt)
        await update_user(message, tags_format=tags_fmt.name)
        tag_value = get_tag_name(tags_fmt.value)
        await message.answer(_('Tags format was changed to {tag_value}').format(tag_value=tag_value))
    else:
        await message.answer(_('Wrong tags format!'))


@dp.message_handler(private_chat, commands=['start', 'help'], state='*')
async def send_welcome(message: types.Message):
    await get_or_create_user_in_db(message)
    langs = ', '.join(settings.langs)
    text = _('<b>Picpack Bot</b>\n'
             'Bot generates description and list of tags for any image. Just send a picture\n'
             'Also it supports link to picture\n'
             'Visite ower site: http://app.picpack.io/demo_en\n'
             'Chat with owner: @FrankShikhaliev\n'
             'Below is a list of available commands, also they could have arguments (in brackets):\n'
             '/lang - change language ({})\n'
             '/tags - change format tags (list, instagram)\n'
             '/rating - rate result on/off (1, 0, on, off)\n'
             '/feedback - leave feedback about our bot').format(langs)
    await message.answer(text)


async def check_edit_keyboard_message(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        async with state.proxy() as data:
            if data.get('inline'):
                await bot.edit_message_text(chat_id=msg.from_user.id,
                                            message_id=msg.message_id-1,
                                            text=_('No action selected!'),
                                            reply_markup=None)
    await state.finish()


@dp.message_handler(private_chat, lambda message: message.text, state=Feedback.leave)
async def update_feedback(message: types.Message, state: FSMContext):
    await update_user(message, bot_feedback=message.text)
    await state.finish()
    await message.answer(_('Thank you for feedback!'))


@dp.message_handler(commands='feedback', state='*')
async def leave_feedback(message: types.Message, state: FSMContext):
    await get_or_create_user_in_db(message)
    await Feedback.leave.set()
    await message.answer(_('Please, leave feedback:'))


@dp.message_handler(group_chat, lambda message: 'image/' in message.document.mime_type,
                    content_types='document', state='*')
@dp.message_handler(group_chat, content_types=['photo'], state='*')
async def group_yandex(message: types.Message):
    group = await get_or_create_group_in_db(message)
    if not group.yandex_token:
        await message.reply(_('No token for Yandex.disk! Please, recieve token:{url}')
                            .format(url=settings.YADISK_AUTH_URL))
        return
    filename, is_url = await form_file_path_url(message)
    if not group.yandex_only_save:
        result = await async_get_desc(path_url=filename,
                                      lang=settings.YADISK_TAG_LANG,
                                      url_method=is_url,
                                      exc_true=False)
    else:
        result = ''
    tag_folder, uuid = make_tag_folder_for_yandex(result)
    upload_success = await yandex_upload(tag=tag_folder,
                                         uuid=uuid,
                                         filename=filename,
                                         token=group.yandex_token)
    answer = await check_answer_yandex(upload_success)
    if answer:
        await message.reply(answer)
    # if upload_success == 'bad_token':
    #     await message.answer(_('Bad Yandex.disk token!'))
    #     return
    # if not upload_success:
    #     await message.answer(_('Error while uploading to Yandex.disk!'))
    # await message.answer(f'upload: {upload_success}')


# @dp.message_handler(ChatTypeFilter(chat_type=['group', 'supergroup', 'private']), commands='hop')
# async def get_commands(message: types.Message):
#     print(message)
#     await message.answer(message)


@dp.message_handler(group_chat, commands='start', state='*')
async def get_commands(message: types.Message):
    await message.answer('start!')


@dp.message_handler(private_chat, lambda message: 'video/' in message.document.mime_type, content_types='document',
                    state='*')
@dp.message_handler(private_chat, content_types=['video'], state='*')
async def video_unsupport(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    await message.answer(_("Sorry, bot doesn't support videos!"))


@dp.message_handler(private_chat, content_types='document', state='*')
async def file_unsupport(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    await message.answer(_("Sorry, bot doesn't support this file format!"))


@dp.message_handler(commands='yadisk_token')
async def set_yadisk_token(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    token = message.get_args()
    if not token:
        await message.reply(_('Token is missing! Should be /yadisk_token YOUR_TOKEN'))
        return
    check_token = await yandex_check(token)
    if not check_token and check_token is not None:
        await message.reply(_('Token is invalid! Please get new one!'))
        return
    if check_token is None:
        text = _('Token was changed, but not verified')
    else:
        text = _('Token was changed and verified')
    if message.chat.id < 0:
        await update_group(message, yandex_token=token)
    else:
        await update_user(message, yandex_token=token)
    print('-'*35)
    
    xxx = await bot.get_chat_member(chat_id=message.chat.id,
                                    user_id=55924337)
    print(f' chat_admin {xxx.is_chat_admin()}')
    op = await bot.get_chat_administrators(chat_id=message.chat.id)
    print(f'count = {len(op)}')
    for i in op:
        print(f'-----{i}')
  
    await message.delete()
    await message.answer(text)



@dp.message_handler(commands='yandex')
async def yandex_turn_on(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    yandex = message.get_args()
    if not yandex:
        yandex = 'on'
    yandex = check_args_bool(yandex)
    if message.chat.id < 0:
        update_group(message, yandex_on=yandex)
    else:
        update_user(message, yandex_on=yandex)
    if yandex:
        text = _('Downloading to Yandex.disk was turned on')
    else:
        text = _('Downloading to Yandex.disk was turned off')
    await message.reply(text)


@dp.message_handler(commands='save_to_yandex_disk')
async def switch_yadisk_mode(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    only_save = message.get_args()
    if not only_save:
        await message.reply(_('No arguments! Should be /save_to_yandex_disk 1/0/on/off'))
        return
    only_save = check_args_bool(only_save)
    if only_save is None:
        await message.reply(_('Bad arguments! Should be /save_to_yandex_disk 1/0/on/off'))
        return
    if message.chat.id < 0:
        update_group(message, yandex_only_save=only_save)
    else:
        update_user(message, yandex_only_save=only_save)
    if only_save:
        text = _('Images will be only save to Yandex.disk')
    else:
        text = _('Images will be with tags and save to Yandex.disk')
    await message.reply(text)


@dp.message_handler(group_chat, commands=['sort', 'save'], state='*')
async def sort_(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    await message.reply(_('Please, reply this message with image'))


@dp.message_handler(private_chat, content_types=['text'], state='*')
async def echo(message: types.Message, state):
    await get_or_create_user_in_db(message)
    await message.answer(_("Don't understand you!"))
