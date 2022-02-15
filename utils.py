"""Utils for bot."""
import logging
import os
import shutil

from aiogram import types

import aiohttp
from aiohttp.client_exceptions import ClientError

from bot_init import _

from config import settings


async def async_get_desc(path_url, lang, tags_format, url_method=False):
    """Select method and get resquest from API."""
    if url_method:
        api_route = settings.url_api
        payload = {'json': {'imageUrl': path_url,
                            'lang': lang}}
    else:
        api_route = settings.file_api
        payload = {'data': {'image_file': open(path_url, 'rb'),
                            'lang': lang}}
    url = settings.url
    url = url + api_route
    result = await async_get_request(url, **payload)
    answer, uuid = make_desc_tags_answer(result, tags_format)
    return answer, uuid


async def async_set_rating(uuid, rating):
    """Set rating for image by uuid."""
    url = settings.url
    url = url + settings.rating_api
    payload = {'exc_true': True,
               'json': {'image_uuid': uuid,
                        'rating': rating}}
    result = await async_get_request(url, **payload)
    if result.get('error'):
        logging.error(f'API rating return err: {result}')


async def async_get_request(url, exc_true=False, **payload):
    timeout = aiohttp.ClientTimeout(connect=settings.ml_models_timeout[0],
                                    sock_read=settings.ml_models_timeout[1])
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=settings.USER_AGENT, **payload) as resp:
                result = await resp.json()
    except (ClientError, ValueError) as e:
        if not exc_true:
            logging.critical(f'API rating error: {e}')
        else:
            raise e
    finally:
        await session.close()
    return result


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
    if tags and len(tags) and (type(tags) == list) > 0:
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
    elif len(tags) == 0:
        answer.append(_('Sorry, tags not found!'))
    else:
        if tags != list:
            answer.append(tags)
        else:
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


def silentremove(path):
    shutil.rmtree(path, ignore_errors=True)


if __name__ == '__main__':
    silentremove('downloads')
