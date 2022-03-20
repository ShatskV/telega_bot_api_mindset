"""Utils for bot."""
import logging
import os
import shutil
import uuid as uuid_lib

import aiohttp
from aiogram import types
from aiohttp.client_exceptions import ClientError

from bot_init import _
from config import settings


async def async_get_desc(path_url, lang, url_method=False, exc_true=None):
    """Select method and get resquest from API."""
    if url_method:
        api_route = settings.url_api
        payload = {'json': {'imageUrl': path_url,
                            'lang': lang}}
    else:
        api_route = settings.file_api
        payload = {'exc_true': exc_true,  # exc_true - raise exc or not
                   'data': {'image_file': open(path_url, 'rb'),
                            'lang': lang}}
    url = settings.url
    url = url + api_route
    result = await async_get_request(url, **payload)
    # answer, uuid = make_desc_tags_answer(result, tags_format)
    return result


async def async_set_rating(uuid, rating):
    """Set rating for image by uuid."""
    url = settings.url
    url = url + settings.rating_api
    payload = {'exc_true': False,
               'json': {'image_uuid': uuid,
                        'rating': rating}}
    result = await async_get_request(url, **payload)
    if result.get('error'):
        logging.error(f'API rating return err: {result}')


async def async_get_request(url, exc_true=True, **payload):
    timeout = aiohttp.ClientTimeout(connect=settings.ml_models_timeout[0],
                                    sock_read=settings.ml_models_timeout[1])
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=settings.USER_AGENT, **payload) as resp:
                result = await resp.json()
    except (ClientError, ValueError) as e:
        result = {'error': 'connection problem!'}
        if not exc_true:
            logging.critical(f'API rating error: {e}')
            return result
        else:
            raise e
    finally:
        await session.close()
    return result


def make_tag_folder_for_yandex(result):
    tag_folder = 'undefined'
    if result.get('error') or not result.get('image_uuid'):
        uuid = uuid_lib.uuid4()
        return tag_folder, uuid
    uuid = result['image_uuid']
    tags = result.get('tags')
    if not tags or tags == [] or (type(tags) == str):
        return tag_folder, uuid
    conf = 0
    for tag in tags:
        if tag['confidence'] > conf:
            tag_folder = tag['tag']
            conf = tag['confidence']
    return tag_folder, uuid


def make_desc_tags_answer(result, tags_format):
    answer = []
    if result.get('error'):
        if result['error'] == 'INVALID_URL':
            error = _('<b>Invalid photo url!<b>')
        else:
            error = _('<b>Service unavailable!</b>')
        answer.append(error)
        return answer, None
    answer.append(_('<b>Description:</b>'))
    if result.get('description'):
        desc = result['description']
        answer.append(desc.capitalize())
    else:
        answer.append(_('Service unavailable!'))
    answer.append(_('<b>Tags:</b>'))
    tags = result.get('tags')
    if tags and len(tags) > 0 and (type(tags) == list):
        i = 0
        answer_tags = ''
        num_tags = len(tags)

        if tags_format == 'list':
            patern = '{},'
        else:
            patern = '#{}'

        for tag in tags:
            tag_value = tag['tag']
            if tags_format == 'instagram':
                tag_value = tag_value.replace(' ', '')
            i += 1
            answer_tags += patern.format(tag_value)
            if i == num_tags:
                if tags_format == 'list':
                    answer_tags = answer_tags[:-1]
                    break
            answer_tags += ' '
        answer.append(answer_tags)
    elif tags is not None and len(tags) == 0:
        answer.append(_('Sorry, tags not found!'))
    else:
        # if tags != list:
        #     answer.append(tags)
        # else:
        answer.append(_('Service unavailable!'))
    return answer, result.get('image_uuid')


async def form_file_path_url(msg: types.Message):
    if msg.text:
        return msg.text, True
    user_path = f'downloads/{msg.from_user.id}'
    os.makedirs(user_path, exist_ok=True)
    if hasattr(msg, 'document') and msg.document is not None:
        file_name = os.path.join(user_path,
                                 f"{msg.document.file_unique_id}.{msg.document.mime_type.split('/')[1]}")
        await msg.document.download(file_name)
    else:
        file_name = os.path.join(user_path, f'{msg.photo[-1].file_id}.jpg')
        await msg.photo[-1].download(file_name)
    return file_name, False


def check_answer_yandex(upload_success):
    if upload_success == 'bad_token':
        return (_('Bad Yandex.disk token! Please, recieve new one: <a href="{url}">Token</a>')
                .format(url=settings.YADISK_AUTH_URL))
    if not upload_success:
        return _('Error while uploading to Yandex.disk!')
    return None


def check_args_bool(args):
    args = args.lower()
    if args in ['0', '1', 'on', 'off']:
        if args in ['1', 'on']:
            return True
        else:
            return False
    else:
        return None


def silentremove(path):
    shutil.rmtree(path, ignore_errors=True)


if __name__ == '__main__':
    silentremove('downloads')
